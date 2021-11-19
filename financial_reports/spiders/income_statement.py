from scrapy.http import Request

from . import MopsSpider
from ..items import IncomeStatementItem


class IncomeStatement(MopsSpider):
    
    name = "income_statement"

    ## Below comments are for test.
    # @property
    # def start_urls(self):
    #     urls = [
    #         'https://emops.twse.com.tw/server-java/t164sb06_e?TYPEK=all&step=show&co_id=2330&year=2020&season=4&report_id=C'
    #     ]
    #     for url in urls:
    #         yield url

    # def start_requests(self):
    #     query_parameters = {
    #         'co_id': '2330',
    #         'year': '2020',
    #         'season': '4',
    #     }
    #     for url in self.start_urls:
    #         yield Request(
    #             url, callback=self.parse,
    #             method='GET', cb_kwargs=query_parameters
    #         )

    def subject_processor(self, value: str) -> str:
        '''
        Data clean function for cleaning subject field
        '''
        process_funcs = [
            self.to_lowercase,
            self.remove_space,
            self.remove_parentheses,
            self.replace_space
        ]
        for func in process_funcs:
            value = func(value)
        return value

    def parse(self, response, **kwargs):
        unit = response.css('.in-w-10::text').getall()[-1]
        unit = self.process_unit(unit)
        # Only use the first table
        table_content = response.css('table.hasBorder')[0]
        # Get all column names
        column_names = table_content.css('tr.in-l-12 > td::text').getall()
        column_names = [self.subject_processor(col_name) for col_name in column_names]
        # Get all rows that we need.
        table_rows = table_content.css('tr:not([class="in-l-12"])')

        for row in table_rows:
            all_rows_tags = row.css('td')
            # Get accounting title
            accounting_title_tag = all_rows_tags.pop(0)
            accounting_title = accounting_title_tag.css('td::text').get()
            accounting_title = self.subject_processor(accounting_title)

            assert len(column_names) == len(all_rows_tags),\
                ValueError((
                    "The length of columns and values should be the same. "
                    "column_names: {}, length: {};"
                    "values: {}, length: {}"
                ).format(column_names, len(column_names), all_rows_tags, len(all_rows_tags)))

            # Populate data into data model.
            for col_name, value_tag in zip(column_names, all_rows_tags):
                income_statement_item = IncomeStatementItem()
                income_statement_item['company_id'] = kwargs['co_id']
                income_statement_item['year'] = kwargs['year']
                income_statement_item['season'] = kwargs['season']
                income_statement_item['accounting_title'] = accounting_title
                income_statement_item['subject'] = col_name
                value = value_tag.css('td::text').get()
                try:
                    value = self.value_processor(value)
                except AttributeError:
                    pass
                income_statement_item['value'] = value
                
                yield income_statement_item

