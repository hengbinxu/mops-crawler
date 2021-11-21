from scrapy.http import Request

from . import MopsSpider
from ..items import CashFlowItem

class CashFlow(MopsSpider):
    
    name = "cash_flow"

    # Below comments are for test.
    # @property
    # def start_urls(self):
    #     urls = [
    #         'https://emops.twse.com.tw/server-java/t164sb05_e?TYPEK=all&step=show&co_id=2330&year=2020&season=4&report_id=C'
    #     ]
    #     for url in urls:
    #         yield url

    # def start_requests(self):
    #     query_parameters = {
    #         'co_id': '2330',
    #         'year': '2020',
    #         'season': 4,
    #     }
    #     for url in self.start_urls:
    #         yield Request(
    #             url, callback=self.parse,
    #             method='GET', cb_kwargs=query_parameters
    #         )

    def subject_processor(self, value: str) -> str:
        process_funcs = [
            self.remove_space,
            self.to_lowercase,
            self.remove_comma,
            self.remove_parentheses,
            self.replace_space,
            self.replace_symbol,
        ]
        for func in process_funcs:
            value = func(value)
        return value

    def subject_reference(self, value: str) -> dict:
        reference = {
            'cash_flows_from_used_in_operating_activities_indirect_method': {
                'category': 'operating',
                'aggregate_subject': 'net_cash_flows_from_used_in_operating_activities'
            },
            'cash_flows_from_used_in_investing_activities': {
                'category': 'investing',
                'aggregate_subject': 'net_cash_flows_from_used_in_investing_activities'
            },
            'cash_flows_from_used_in_financing_activities': {
                'category': 'financing',
                'aggregate_subject': 'net_cash_flows_from_used_in_financing_activities'
            },
        }
        return reference[value]

    def parse(self, response, **kwargs):
        unit = response.css('.in-w-10::text').getall()[-1]
        unit = self.process_unit(unit)
        table_rows = response.css('table.hasBorder > tr:not([class="bl-d-12"])')
        category, agg_subject = '', ''
        for row in table_rows:
            cash_flow_item = CashFlowItem()
            cash_flow_item['company_id'] = kwargs['co_id']
            cash_flow_item['year'] = kwargs['year']
            cash_flow_item['season'] = kwargs['season']
            cash_flow_item['unit'] = unit
            row_values = row.css('td::text').getall()
            if len(row_values) == 1:
                subject = self.subject_processor(row_values[0])
                refer_info = self.subject_reference(subject)
                category = refer_info['category']
                agg_subject = refer_info['aggregate_subject']
                continue

            # Extract data and clean data
            subject, value, _ = row_values
            subject = self.subject_processor(subject)
            value = self.value_processor(value)

            # Populate data into data model
            cash_flow_item['category'] = category
            cash_flow_item['subject'] = subject
            cash_flow_item['value'] = value

            if agg_subject == subject:
                # Reset category
                category = ''

            yield cash_flow_item


# Cash Flow:
#   formula => Cash-Flow = operating_activities + investing_activities + financing_activities
# Reference:
# https://www.investopedia.com/investing/what-is-a-cash-flow-statement/