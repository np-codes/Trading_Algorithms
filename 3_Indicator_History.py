'''This strategy trades the SPY ETF using a combination of a custom 30-day 
Simple Moving Average (SMA) and the 52-week high and low prices. It enters 
long positions when the price exceeds the 52-week high by 5% and the SMA is 
below the current price, and enters short positions when the price falls below 
the 52-week low by 5% and the SMA is above the current price. Positions are 
liquidated if the conditions for entry are no longer met'''

# Concept: Using Indicators + History Request (data pumping in indicator)

# region imports
from AlgorithmImports import *
from collections import deque
from datetime import datetime, timedelta
# endregion

class FormalBlueMosquito(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2024, 1, 1)
        self.set_cash(100000)
        self.spy = self.add_equity("SPY", Resolution.DAILY).symbol

        # Custom Indicator Calling
        self.indicatorSMA = CustomSimpleMovingAverage("CustomSMA", 30)
        self.RegisterIndicator(self.spy, self.indicatorSMA, Resolution.DAILY)
        
    '''    self.indicatorSMA = self.sma(self.spy, 30, Resolution.DAILY)

        # Pumping data in indicator (making it ready)
        # [ this means you dont need to check indicator is_ready ]
        closingPrice = self.history(self.spy, 30, Resolution.DAILY)["close"]
        for time, price in closingPrice.loc[self.spy].items() :
            self.indicatorSMA.update(time, price)
    '''
        
    def on_data(self, data: Slice):
        if not self.indicatorSMA.is_ready :
            return
        hist = self.history(self.spy, timedelta(365), Resolution.DAILY)
        low = min(hist["low"])
        high = max(hist["high"])

        spyPrice = self.securities[self.spy].price

        if spyPrice * 1.05 >= high and self.indicatorSMA.current.value < spyPrice :
            if not self.portfolio[self.spy].is_long :
                self.set_holdings(self.spy, 1)

        elif spyPrice * 0.95 <= low and self.indicatorSMA.current.value > spyPrice:
            if not self.portfolio[self.spy].is_short :
                self.set_holdings(self.spy, -1)

        else:
            self.liquidate()

        self.plot("Benchmark", "52w-High", high)
        self.plot("Benchmark", "52w-Low", low)
        self.plot("Benchmark", "SMA", self.indicatorSMA.current.value)

# Creating custom indicator
class CustomSimpleMovingAverage(PythonIndicator):

    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min
        self.Value = 0
        self.queue = deque(maxlen=period)
        # if one is looking for 30 day moving average the queue will save upto 30 elements

    def update(self, input) :
        self.queue.appendleft(input.Close) # older closing price on right 
        self.Time = input.EndTime
        count = len(self.queue)
        self.Value = sum(self.queue) / count
        return (count == self.queue.maxlen)
    
