# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field


class TWFiftyItem(scrapy.Item):
    company_id = Field()
    company_name = Field()
    weight = Field()


class IncomeStatementItem(scrapy.Item):
    pass


class BalanceSheetItem(scrapy.Item):
    pass


class CashFlowItem(scrapy.Item):
    pass

