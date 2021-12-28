from scrapy.http import Request

from . import MopsSpider
from ..items import IncomeStatementItem


class IncomeStatement(MopsSpider):
    
    name = "income_statement"

    pipeline = {
        "CsvExportPipeline",
        # "MultiExportPipeline",
    }

    _reference = {
        'operating_expenses': {
            'aggregate_subject': 'total_operating_expenses',
        },
        'non_operating_income_and_expenses': {
            'aggregate_subject': 'total_non_operating_income_and_expenses',
        },
        'other_comprehensive_income': {
            'aggregate_subject': 'total_comprehensive_income',
        },
        'profit_loss_attributable_to:': {
            'aggregate_subject': None
        },
        'basic_earnings_per_share': {
            'aggregate_subject': 'total_basic_earnings_per_share'
        },
        'diluted_earnings_per_share': {
            'aggregate_subject': 'total_diluted_earnings_per_share'
        },
    }

    # Below comments are for test.
    # @property
    # def start_urls(self):
    #     urls = [
    #         'https://emops.twse.com.tw/server-java/t164sb04_e?TYPEK=all&step=show&co_id=2330&year=2020&season=4&report_id=C',
    #         'https://emops.twse.com.tw/server-java/t164sb04_e?TYPEK=all&step=show&co_id=2303&year=2015&season=4&report_id=C',
    #         'https://emops.twse.com.tw/server-java/t164sb04_e?co_id=5546&year=2016&season=4&step=show&TYPEK=all&report_id=C' # No data example
    #     ]
    #     for url in urls:
    #         yield url

    # def start_requests(self):
    #     query_parameters = [
    #         {'co_id': '2330', 'year': '2020', 'season': '4'},
    #         {'co_id': '2303', 'year': '2020', 'season': '4'},
    #         {'co_id': '5546', 'year': '2020', 'season': '4'},
    #     ]
    #     for url, params in zip(self.start_urls, query_parameters):
    #         yield Request(
    #             url, callback=self.parse,
    #             method='GET', cb_kwargs=params
    #         )

    def subject_reference(self, value: str) -> dict:
        return self._reference[value]

    def subject_processor(self, value: str) -> str:
        '''
        Data clean function for cleaning subject field
        '''
        process_funcs = [
            self.to_lowercase,
            self.remove_space,
            self.remove_comma,
            self.remove_parentheses,
            self.spaces_to_splace,
            self.replace_space,
        ]
        for func in process_funcs:
            value = func(value)
        return value

    def parse(self, response, **kwargs):
        try:
            unit = response.css('.in-w-10::text').getall()[-1]
        except IndexError:
            self.logger.info((
                "The response doesn't have any data.\n"
                "Request URL: {}\nquery_parameters: {}"
            ).format(response.url, kwargs))
            return None

        unit = self.process_unit(unit)
        # Get rows that we want to extract.
        table_rows = response.css('table.hasBorder > tr:not([class="bl-d-12"])')

        # List the subjects, if it doesn't have value, it will ignore to record.
        ignore_subjects = {
            'profit_loss', 'net_operating_income_loss'
        }
        category, agg_subject = '', ''
        for row in table_rows:
            income_statement_item = IncomeStatementItem()
            income_statement_item['company_id'] = kwargs['co_id']
            income_statement_item['year'] = kwargs['year']
            income_statement_item['season'] = kwargs['season']
            income_statement_item['request_url'] = kwargs['request_url']
            income_statement_item['unit'] = unit
            row_values = row.css('td::text').getall()        
            if len(row_values) == 1 and\
                self.subject_processor(row_values[0]) in self._reference:
                category = self.subject_processor(row_values[0])
                refer_info = self.subject_reference(category)
                agg_subject = refer_info['aggregate_subject']
                continue

            try:
                subject, value, _ = row_values
            except ValueError:
                subject, *_ = row_values

                if subject in ignore_subjects:
                    continue
                else:
                    value = ''

            subject = self.subject_processor(subject)
            value = self.value_processor(value)
            income_statement_item['category'] = category
            income_statement_item['subject'] = subject
            income_statement_item['value'] = value

            # Reset category
            if subject == agg_subject:
                category = ''

            yield income_statement_item

