'''This strategy selects a dynamic stock portfolio by filtering the top 200 
stocks by dollar volume and further refining to 10 based on market 
capitalization. It rebalances monthly, adjusts targets proportionally, and 
liquidates removed securities.'''

# Concept: Creating Dynamic Universe
from AlgorithmImports import *
from datetime import datetime, timedelta

class UglyYellowGreenChinchilla(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2024, 1, 1)
        self.set_cash(10000)

        self.rebalanceTime = datetime.min
        self.activeStocks = set()
        self.add_universe(self.coarse_filter, self.fine_filter)
        self.universe_settings.resolution = Resolution.HOUR

        self.portfolioTargets = []

    def coarse_filter(self, coarse):
        if self.time <= self.rebalanceTime:
            return self.universe.unchanged
        self.rebalanceTime = self.time + timedelta(days=30)
        sorted_by_dollar_volume = sorted(coarse, key=lambda x: x.dollar_volume, reverse=True)
        return [x.symbol for x in sorted_by_dollar_volume if x.price > 10 and x.has_fundamental_data][:200]

    def fine_filter(self, fine):
        sorted_by_p_e = sorted(fine, key=lambda x: x.market_cap)
        return [x.symbol for x in sorted_by_p_e if x.market_cap > 0][:10]

    def on_securities_changed(self, changes):
        for x in changes.removed_securities:
            self.liquidate(x.symbol)
            self.activeStocks.remove(x.symbol)

        for x in changes.added_securities:
            self.activeStocks.add(x.symbol)

        self.portfolioTargets = [PortfolioTarget(symbol, 1/len(self.activeStocks)) for symbol in self.activeStocks]

    def on_data(self, data: Slice):
        if not self.portfolioTargets:
            return

        for symbol in self.activeStocks:
            if symbol not in data:
                return

        for target in self.portfolioTargets:
            self.set_holdings(target.symbol, target.quantity)
        self.portfolioTargets = []