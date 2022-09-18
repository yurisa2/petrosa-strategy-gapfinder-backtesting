from backtesting import Strategy, Backtest
from app import get_data
import numpy as np
from backtesting.lib import plot_heatmaps


test_period = '30m'

data_strat = get_data.get_data('SOLUSDT', test_period, 130)
data = get_data.get_data('SOLUSDT', '5m', 700)

data
data_strat.loc[data_strat.index < '2022-09-16 19:00:00']

'2022-09-16 19:00:00' in data_strat.index
data.index[-6]


class bb_backtest(Strategy):
    buy_sl = 2
    buy_tp = 2
    sell_sl = 2
    sell_tp = 2
    buy_threshold = 2
    sell_threshold = 2
    sell_enabled = True
    buy_enabled = True

    def init(self):
        pass

    def next(self):

        try:
            if(self.data.index[-1] in self.main_data.index):
                work_data = self.main_data.loc[self.main_data.index <= self.data.index[-1]]
                print('work_data', work_data.index[-1])
                print('main_Data', self.data.index[-1])
        except Exception as e:
            print(e)
            # print(self.data)
            # print(self.data.Close[-1])


strat = bb_backtest

strat.main_data = data_strat

bt = Backtest(
                data,
                strat,
                commission=0,
                exclusive_orders=True,
                cash=100000)


el_run = bt.run()
