'''This strategy trades SPY using a simple entry and exit rule. It enters a 
position when the next entry time arrives and the portfolio isn't invested. It 
then holds the position until the price increases or decreases by 10% from the 
entry price, at which point it sells. The strategy uses a cooldown period of 5 
days before allowing another entry.'''

# Concept: Entery-Exit Logic + Cooldown Period

# region imports
from AlgorithmImports import *
from QuantConnect.Data import Slice
from datetime import datetime, timedelta
# endregion

class SleepySkyBlueGiraffe(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2023, 1, 8)
        self.set_end_date(2024, 1, 8)
        self.set_cash(1000)
        spy = self.add_equity("SPY", Resolution.DAILY)
        # self.add_forex, self.add_future ..

        spy.set_data_normalization_mode(DataNormalizationMode.RAW)
        self.spy = spy.symbol
        self.set_benchmark("SPY")
        self.set_brokerage_model(BrokerageName.INTERACTIVE_BROKERS_BROKERAGE, AccountType.MARGIN)
        self.entryPrice = 0
        self.period = timedelta(5)
        self.nextEntryTime = self.time

    def on_data(self, data: Slice):
        if not self.spy in data.bars:
            return
       
        price = data.Bars[self.spy].Close
        #price = data[self.spy].Close
        #price = self.securities(self.spy).Close

        if not self.portfolio.invested:
            if self.nextEntryTime <= self.time:
                self.set_holdings(self.spy, 1)
                #self.market_order(self.spy, int(self.portfolio.set_cash / price))
                self.Log("BUY SPY @" + str(price))
                self.entryPrice = price

        elif self.entryPrice * 1.1 < price or self.entryPrice * 0.9 > price:
            self.liquidate()
            self.log("Sell SPY @" + str(price))
            self.nextEntryTime = self.time + self.period