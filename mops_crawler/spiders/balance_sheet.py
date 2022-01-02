from scrapy.http import Request
from . import MopsSpider

from ..items import BalanceSheetItem

class BalanceSheet(MopsSpider):
    
    name = "balance_sheet"

    pipeline = {
        "CsvExportPipeline",
        # "MultiExportPipeline",
    }
    # Define the order of export fileds
    _export_fields = [
        'company_id', 'year', 'season', 'component',
        'category', 'sub_category', 'subject', 'value',
        'request_url'
    ]

    # Below are for test
    # start_urls = [
    #     # 'https://emops.twse.com.tw/server-java/t164sb03_e?TYPEK=all&step=show&co_id=2330&year=2020&season=4&report_id=C',
    #     # 'https://emops.twse.com.tw/server-java/t164sb03_e?co_id=2881&year=2019&season=4&step=show&TYPEK=all&report_id=C',
    #     # 'https://emops.twse.com.tw/server-java/t164sb03_e?co_id=2867&year=2019&season=4&step=show&TYPEK=all&report_id=C',
    #     # 'https://emops.twse.com.tw/server-java/t164sb03_e?co_id=2897&year=2017&season=4&step=show&TYPEK=all&report_id=C',
    #     # 'https://emops.twse.com.tw/server-java/t164sb03_e?co_id=3338&year=2018&season=4&step=show&TYPEK=all&report_id=C',
    #     # 'https://emops.twse.com.tw/server-java/t164sb03_e?co_id=5220&year=2015&season=4&step=show&TYPEK=all&report_id=C'
    # ]

    # query_parameter = [
    #     # {'co_id': '2330', 'year': '2020', 'season': '4'},
    #     # {'co_id': '2881', 'year': '2019', 'season': '4'},
    #     # {'co_id': '2867', 'year': '2019', 'season': '4'},
    #     # {'co_id': '2897', 'year': '2016', 'season': '4'},
    #     # {'co_id': '3338', 'year': '2018', 'season': '4', 'step': 'show', 'TYPEK': 'all', 'report_id': 'C'},
    #     # {'co_id': '5220', 'year': '2015', 'season': '4', 'step': 'show', 'TYPEK': 'all', 'report_id': 'C'},
    # ]

    # def start_requests(self):
    #     for url, request_info in zip(self.start_urls, self.query_parameter):
    #         yield Request(
    #             url, callback=self.parse,
    #             method='GET', cb_kwargs=request_info
    #         )

    def subject_processor(self, value: str) -> str:
        '''
        Data clear function to clean subjects.
        '''
        process_funcs = [
            self.remove_space,
            self.to_lowercase,
            self.replace_symbol,
            self.remove_quotation,
            self.spaces_to_splace,
            self.replace_space,
        ]
        for func in process_funcs:
            value = func(value)
        return value

    def subject_reference(self, value: str) -> dict:
        '''
        Get subject belong to which component, and its aggregation subject name.
        The aggregation subject name is as a flag to note that the component needs to be reset.
        '''
        reference = {
            'current_assets': {
                'component': 'assets', 'aggregate_subject': 'total_assets'
            },
            'non_current_assets': {
                'component': 'assets', 'aggregate_subject': 'total_assets'
            },
            'current_liabilities': {
                'component': 'liabilities', 'aggregate_subject': 'total_liabilities'
            },
            'non_current_liabilities': {
                'component': 'liabilities', 'aggregate_subject': 'total_liabilities'
            },
            'equity_attributable_to_owners_of_parent': {
                'component': 'equity', 'aggregate_subject': 'total_equity'
            },
            # Below are for handling more exception
            'assets': {
                'component': 'assets', 'aggregate_subject': 'total_assets'
            },
            'liabilities': {
                'component': 'liabilities', 'aggregate_subject': 'total_liabilities'
            },
            'stockholders_equity': {
                'component': 'equity', 'aggregate_subject': 'total_stockholders_equity'
            },
            'liabilities_and_equity': {
                'component': 'liabilities_and_equity', 'aggregate_subject': 'total_liabilities_and_equity'
            },
            # 'share_capital': {
            #     'component': 'equity', 'aggregate_subject': 'total_share_capital'
            # },
            # 'capital_surplus': {
            #     'component': 'equity', 'aggregate_subject': 'total_capital_surplus'
            # },
            # 'retained_earnings': {
            #     'component': 'equity', 'aggregate_subject': 'total_retained_earnings'
            # }
        }
       
        return reference[value]

    def parse(self, response, **kwargs):
        try:
            unit = response.css('.in-w-10::text').getall()[-1]
        except IndexError:
            self.logger.info((
                "The response doesn't have any data.\n"
                "Request URL: {}\nquery_parameters: {}"
            ).format(response.url, kwargs))
            return None

        # unit = self.process_unit(unit)
        table_rows = response.css('.hasBorder > tr:not([class="bl-d-12"])')
        reset_component = False
        refer_info = {'component': None, 'aggregate_subject': None}
        component, category, sub_category, subject = ['', '', '', '']
        for row in table_rows:
            balance_sheet_item = BalanceSheetItem()
            balance_sheet_item['company_id'] = kwargs['co_id']
            balance_sheet_item['year'] = kwargs['year']
            balance_sheet_item['season'] = kwargs['season']
            balance_sheet_item['request_url'] = kwargs['request_url']
            # balance_sheet_item['unit'] = unit
            # Extract data from each row
            row_values = row.css('td::text').getall()
            if len(row_values) == 1:
                if component == 'equity':
                    # Only equity has sub_category.
                    sub_category = self.subject_processor(row_values[0])
                else:
                    category = self.subject_processor(row_values[0])
                    refer_info = self.subject_reference(category)
                    component = refer_info['component']
                continue

            subject, value, _ = row_values
            subject = self.subject_processor(subject)
            value = self.value_processor(value)

            # The aggregate subject doesn't belong to any category and sub_category.
            if subject == refer_info['aggregate_subject']:
                reset_component = True
                category, sub_category = '', ''

            balance_sheet_item['component'] = component
            balance_sheet_item['category'] = category
            balance_sheet_item['sub_category'] = sub_category
            balance_sheet_item['subject'] = subject
            balance_sheet_item['value'] = value

            # After aggregate subject, it needs to reset component.
            if reset_component:
                component = ''
                reset_component = False

            yield balance_sheet_item

# Balance Sheet:
#   formula => Assets = Liabilities + Shareholder Equity
# Reference:
# https://www.investopedia.com/terms/b/balancesheet.asp
