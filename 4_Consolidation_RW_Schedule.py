'''This strategy trades SPY using a daily consolidation of price data. It 
opens a short position if the opening price is 1% higher than the previous 
day's close and a long position if it is 1% lower. The positions are exited at 
the end of the day using a scheduled liquidation.'''

# Concept used: Consolidation + Rolling Window + Scheduling Events

# region imports
from AlgorithmImports import *
# endregion

class FatBlackEagle(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2024, 1, 1)
        self.set_cash(100000)
        self.spy = self.add_equity("SPY", Resolution.MINUTE).symbol
        self.rollingWindow = RollingWindow[TradeBar](2)
        self.consolidate(self.spy, Resolution.DAILY, self.CustomBarHandler)
        self.schedule.on(self.date_rules.every_day(self.spy), self.time_rules.before_market_close(self.spy, 15), self.ExitPositions)

    def on_data(self, data: Slice):
        if not self.rollingWindow.is_ready :
            return

        if not (self.time.hour == 9 and self.time.minute == 31) :
            return

        # Gap Up => Sell
        if data[self.spy].open >= 1.01 * self.rollingWindow[0].close :
            self.set_holdings(self.spy, -1)
        # Gap Down => Buy
        elif data[self.spy].open <= 0.99 * self.rollingWindow[0].close :
            self.set_holdings(self.spy, 1)

    def CustomBarHandler(self, bar) :
        self.rollingWindow.add(bar)

    def ExitPositions(self) :
        self.liquidate(self.spy)