from . import MopsSpider

class BalanceSheet(MopsSpider):
    
    name = "balance_sheet"
    
    def parse(self, response, **kwargs):
        pass