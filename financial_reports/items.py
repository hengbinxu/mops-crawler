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


class BaseItem(scrapy.Item):
    company_id = Field()
    year = Field()
    season = Field()
    unit = Field()


class BalanceSheetItem(BaseItem):
    category = Field()
    sub_categiry = Field()
    subject = Field()
    value = Field()


class IncomeStatementItem(BaseItem):
    pass



class CashFlowItem(BaseItem):
    pass

