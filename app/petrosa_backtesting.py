import os
import json
import datetime
import time
import logging 
import numpy as np
import pymongo
from backtesting import Strategy, Backtest
from app import get_data
from backtesting.lib import plot_heatmaps
import newrelic.agent



class bb_backtest(Strategy):
    buy_sl = None
    buy_tp = None
    sell_sl = None
    sell_tp = None
    buy_threshold = None
    sell_threshold = None
    sell_enabled = True
    buy_enabled = True

    def init(self):
        pass


    @newrelic.agent.background_task()
    def next(self):

        if (
            self.buy_sl is None
            or self.buy_tp is None
            or self.sell_sl is None
            or self.sell_tp is None
            or self.buy_threshold is None
            or self.sell_threshold is None
            or self.sell_enabled is None
            or self.buy_enabled is None
        ):
            return True

        if(self.buy_sl > self.buy_tp
                or self.sell_sl > self.sell_tp):
            return True

        try:
            if(self.data.index[-1] in self.main_data.index):
                work_data = self.main_data.loc[self.main_data.index
                                               <= self.data.index[-1]]
                # print('work_data', work_data.index[-1])
                # print('main_Data', self.data.index[-1

                # print(self.data.index[-1])
                diff = ((work_data.Close[-1] / work_data.Close[-2])-1)*100
                if diff > (-1 * self.sell_threshold) and self.sell_enabled:
                    buy_sl = work_data.Close[-1] * (1 - (self.buy_sl / 100))
                    buy_tp = work_data.Close[-1] * (1 + (self.buy_tp / 100))
                    self.buy(sl=buy_sl, tp=buy_tp)
                if diff < self.buy_threshold and self.buy_enabled:
                    sell_sl = work_data.Close[-1] * (1 + (self.sell_sl / 100))
                    sell_tp = work_data.Close[-1] * (1 - (self.sell_tp / 100))
                    self.sell(sl=sell_sl, tp=sell_tp)

            else:
                return True

        except Exception as e:
            pass


@newrelic.agent.background_task()
def run_backtest(symbol, test_period):

    data = get_data.get_data(symbol, '5m')
    main_data = get_data.get_data(symbol, test_period)

    strat = bb_backtest
    strat.main_data = main_data

    bt = Backtest(
                    data,
                    strat,
                    commission=0,
                    exclusive_orders=True,
                    cash=100000)

    stats, heatmap = bt.optimize(
        buy_sl=list(np.arange(0.2, 2, 1)),
        buy_tp=list(np.arange(0.2, 2, 1)),
        sell_sl=list(np.arange(0.2, 2, 1)),
        sell_tp=list(np.arange(0.2, 2, 1)),
        buy_threshold=list(np.arange(0.2, 1, 1)),
        sell_threshold=list(np.arange(0.2, 1, 1)),
        # sell_enabled=[True, False],
        # buy_enabled=[True, False],
        maximize='SQN',
        # minimize='Max. Drawdown [%]',
        max_tries=2000,
        random_state=0,
        return_heatmap=True)
    # plot_heatmaps(heatmap, agg='mean')

    client = pymongo.MongoClient(
                os.getenv(
                    'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
                readPreference='secondaryPreferred',
                appname='petrosa-strategy-backtest-simple-gap-finder'
                                        )

    heatmap = heatmap.dropna().sort_values().iloc[-10:]
    new_hm = {}
    new_hm['heatmap'] = heatmap
    new_hm['insert_timestamp'] = datetime.datetime.now()
    new_hm['strategy'] = 'simple_gap_finder'
    new_hm['period'] = test_period
    new_hm['symbol'] = symbol

    doc = json.dumps({**stats._strategy._params,
                     ** stats, **new_hm}, default=str)
    doc = json.loads(doc)

    client.petrosa_crypto['backtest_results'].update_one(
                                            {"strategy": "simple_gap_finder",
                                             "symbol": symbol,
                                             "period": test_period
                                             }, {"$set": doc}, upsert=True)


@newrelic.agent.background_task()
def continuous_run():
    client = pymongo.MongoClient(
                os.getenv(
                    'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
                readPreference='secondaryPreferred',
                appname='petrosa-strategy-backtest-simple-gap-finder'
                                        )
    try:
        params = client.petrosa_crypto['backtest_controller'].find_one(
            {"status": 0, "strategy": "simple_gap_finder"})
        client.petrosa_crypto['backtest_controller'].update_one(
            params, {"$set": {"status": 1}})

        logging.warning('Running backtest for simple_gap_finder on: ' + str(params))
        run_backtest(params['symbol'], params['period'])

        client.petrosa_crypto['backtest_controller'].update_one(
            {"_id": params['_id']}, {"$set": {"status": 2}})

        logging.warning('Finished ' + str(params))

        pass
    except Exception as e:
        logging.error(e)
        time.sleep(10)

# bt.run()
