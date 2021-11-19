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


class CompanyInfoItem(scrapy.Item):
    market = Field()
    company_id = Field()
    company_name = Field()
    place_of_incorporation_of_foreign_companies = Field()
    industry = Field()
    symbol = Field()
    date_of_listing = Field()
    chariman = Field()
    general_manager = Field()
    spokesman = Field()
    title_of_spokersman = Field()
    fiscal_year_end = Field()
    accounting_firm = Field()
    cpa_1 = Field()
    cpa_2 = Field()
    address = Field()
    telephone = Field()
    fax = Field()
    email = Field()
    web_address = Field()
    investor_relations_contact_person = Field()
    title_of_ir_contact_person = Field()
    telephon_of_ir_contact_person = Field()
    email_of_ir_contact_person = Field()


class BaseItem(scrapy.Item):
    company_id = Field()
    year = Field()
    season = Field()
    unit = Field()


class BalanceSheetItem(BaseItem):
    component = Field()
    category = Field()
    sub_category = Field()
    subject = Field()
    value = Field()


class CashFlowItem(BaseItem):
    category = Field()
    subject = Field()
    value = Field()


class IncomeStatementItem(BaseItem):
    accounting_title = Field()
    subject = Field()
    value = Field()




