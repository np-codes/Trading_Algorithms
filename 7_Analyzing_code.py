'''
This strategy uses an SMA to identify trends and dynamically allocates 80/
20 between SPY and BND based on market conditions, rebalancing every 30 days.
'''

# Concept: Backtesting + Analyzing Result + Parameter usage + Optimizing

# region imports
from AlgorithmImports import *
from datetime import datetime, timedelta
# endregion

class SmoothMagentaDolphin(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2022, 1, 1)
        self.set_end_date(2025,1,1)
        self.set_cash(100000)
        self.spy = self.add_equity("SPY", Resolution.DAILY).symbol
        self.bnd = self.add_equity("BND", Resolution.DAILY).symbol

        # Using parameter which can also be optimize (paid feature in quantconnect)
        length = self.get_parameter("sma_length")
        length = 30 if length is None else int(length)

        # Instead of length we used to type 30
        self.indicatorSMA = self.sma(self.spy, length, Resolution.DAILY)
        self.rebalanceTime = datetime.min
        self.uptrend = True

    def on_data(self, data: Slice):
        if not self.indicatorSMA.is_ready or self.spy not in data or self.bnd not in data:
            return
        
        if data[self.spy].price >= self.indicatorSMA.current.value:
            if self.time >= self.rebalanceTime or not self.uptrend:
                self.set_holdings(self.spy,0.8)
                self.set_holdings(self.bnd,0.2)
                self.uptrend = True
                self.rebalanceTime = self.time + timedelta(30)

        elif self.time >= self.rebalanceTime or self.uptrend:
                self.set_holdings(self.spy,0.2)
                self.set_holdings(self.bnd,0.8)
                self.uptrend = False
                self.rebalanceTime = self.time + timedelta(30)
        
        self.plot("Benchmark", "SMA", self.indicatorSMA.current.value)