'''This trading strategy analyzes Elon Musk's tweets using sentiment analysis 
to determine Tesla stock positions. Positive tweets trigger buys, negative 
ones trigger sells, and positions are exited daily before market close.'''

# Concept: Adding Custom Data

# region imports
from AlgorithmImports import *
from datetime import datetime, timedelta
from nltk.sentiment import SentimentIntensityAnalyzer # type: ignore
# endregion
debugfn = None # global debugger to use in different class
class EmotionalFluorescentYellowScorpion(QCAlgorithm):

    def initialize(self):
        global debugfn
        debugfn = self.debug
        self.set_start_date(2022, 7, 1)
        self.set_end_date(2023,10,1)
        self.set_cash(100000)
        self.tsla = self.add_equity("TSLA", Resolution.MINUTE).symbol
        self.musk = self.add_data(MuskTweet, "MUSKTWTS", Resolution.MINUTE).symbol
        self.schedule.on(self.date_rules.every_day(self.tsla), self.time_rules.before_market_close(self.tsla,15), self.ExitPositions)

    def on_data(self, data: Slice):
        if self.musk in data:
            score = data[self.musk].value
            content = data[self.musk].Tweet

            if score > 0.5:
                self.set_holdings(self.tsla,1)
            elif score < -0.5:
                self.set_holdings(self.tsla, -1)
            
            if abs(score) > 0.5:
                self.log(f"Score: {str(score)} , Tweet: {content}")
    
    def ExitPositions(self):
        self.liquidate()

class MuskTweet(PythonData):

    sia = SentimentIntensityAnalyzer()
    def get_source(self, config, date, is_live_mode):
        source = "https://www.dropbox.com/scl/fi/drn5fjyyyscaqkk913wox/elon_musk_tweets_PreProcessed.csv?rlkey=mga8or9sp0v5h8ah31ef5jaah&st=sfcrdpnn&dl=1"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.REMOTE_FILE)
    
    def reader(self, config, line, date, is_live_mode):
        global debugfn
        if not (line.strip() and line[0].isdigit()):
            return None
        data = line.split(",")
        tweet = MuskTweet()
        
        try:
            tweet.symbol = config.symbol
            tweet.time = datetime.strptime(data[0], "%m-%d-%Y %H:%M:%S" ) + timedelta(minutes=1)
            content = data[1].lower()
            if "tsla" in content or "tesla" in content :
                tweet.value = self.sia.polarity_scores(content)["compound"]
            else:
                tweet.value = 0
            tweet["Tweet"] = str(content)
        except ValueError:
            return None
        return tweet