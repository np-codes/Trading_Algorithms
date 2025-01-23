'''This strategy trades QQQ using a limit order for entry and a trailing 
stop-loss that sells the stock if the price drops by 5% (stop price adjusts to 
95% of the highest price). The limit price is adjusted if the order remains 
unfilled for a day, and there is a 15-day cooldown after exiting a position.
'''

# Concept: Limit Trailing (Limit Order) + Position Sizing 

# region imports
from AlgorithmImports import *
# endregion

class UglyTanPelican(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2024, 1, 1)
        self.set_end_date(2025, 1, 1)
        self.set_cash(1000)

        self.qqq = self.add_equity("QQQ", Resolution.Hour).symbol
        
        self.entryTicket = None
        self.stopMarketTicket = None
        self.entryTime = self.time
        self.stopMarketOrderFillTime = self.time
        self.highestPrice = 0 

    def on_data(self, data: Slice):

        # wait 30 days after last exit
        if (self.time - self.stopMarketOrderFillTime).days < 15 :
            return

        currentPrice = self.Securities[self.qqq].Price 

        # send entry limit order
        if not self.portfolio.invested and not self.transactions.get_open_orders(self.qqq) :
            quantity = self.calculate_order_quantity(self.qqq, 0.9)
            self.entryTicket = self.limit_order(self.qqq, quantity, currentPrice , "Entry Order")
            self.entryTime = self.time

        # move limit price if not filled after 1 day
        if(self.time - self.entryTime).days > 1 and self.entryTicket is not None and self.entryTicket.status != OrderStatus.FILLED:
            self.entryTime = self.time
            updateFields = UpdateOrderFields()
            updateFields.limit_price = currentPrice
            self.entryTicket.update(updateFields)

        # move up trailing stop price
        if self.stopMarketTicket is not None and self.portfolio.invested :
            if currentPrice > self.highestPrice:
                self.highestPrice = currentPrice
                updateFields = UpdateOrderFields()
                updateFields.stop_price = currentPrice * 0.95
                self.stopMarketTicket.update(updateFields)

    def on_order_event(self, order_event):
        if order_event.status != OrderStatus.FILLED :
            return

        # send stop loss order if entry limit order is filled
        if self.entryTicket is not None and self.entryTicket.order_id == order_event.order_id:
            self.stopMarketTicket = self.stop_market_order(self.qqq, -self.entryTicket.quantity, 0.95 * self.entryTicket.average_fill_price,"Sell Order")

        # save fill time of stop loss order
        if self.stopMarketTicket is not None and self.stopMarketTicket.order_id == order_event.order_id :
            self.stopMarketOrderFillTime = self.time
            self.highestPrice = 0