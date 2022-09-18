from backtesting import Strategy, Backtest
from app import get_data
import numpy as np
from backtesting.lib import plot_heatmaps


test_period = '30m'

data = get_data.get_data('SOLUSDT', test_period, 1500)

diff_test = []


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

        if (
            self.buy_sl is None
            or self.buy_tp is None
            or self.sell_sl is None
            or self.sell_tp is None
            or self.buy_threshold is None
            or self.sell_threshold is None
        ):
            return True

        # print(self.data.index[-1])
        diff = ((self.data.Close[-1] / self.data.Close[-2])-1)*100
        if diff < (-1 * self.sell_threshold) and self.sell_enabled:
            buy_sl = self.data.Close[-1] * (1 - (self.buy_sl / 100))
            buy_tp = self.data.Close[-1] * (1 + (self.buy_tp / 100))
            self.buy(sl=buy_sl, tp=buy_tp)
        if diff > self.buy_threshold and self.buy_enabled:
            sell_sl = self.data.Close[-1] * (1 + (self.sell_sl / 100))
            sell_tp = self.data.Close[-1] * (1 - (self.sell_tp / 100))
            self.sell(sl=sell_sl, tp=sell_tp)


strat = bb_backtest
bt = Backtest(
                data,
                strat,
                commission=0,
                exclusive_orders=True,
                cash=100000)


stats, heatmap = bt.optimize(
    buy_sl=list(np.arange(0.2, 2, 0.5)),
    buy_tp=list(np.arange(0.2, 2, 0.5)),
    sell_sl=list(np.arange(0.2, 2, 0.5)),
    sell_tp=list(np.arange(0.2, 2, 0.5)),
    buy_threshold=list(np.arange(0.2, 1, 0.5)),
    sell_threshold=list(np.arange(0.2, 1, 0.5)),
    # sell_enabled=[True, False],
    # buy_enabled=[True, False],
    maximize='SQN',
    # minimize='Max. Drawdown [%]',
    max_tries=2000,
    random_state=0,
    return_heatmap=True)
# plot_heatmaps(heatmap, agg='mean')

heatmap.dropna().sort_values().iloc[-100:]


# bt.run()
