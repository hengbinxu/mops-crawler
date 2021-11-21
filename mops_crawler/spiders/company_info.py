from typing import Generator

from scrapy import Spider
from scrapy.http import FormRequest

from ..items import CompanyInfoItem

class CompanyInfo(Spider):
    '''
    Get Taiwan all company information.
    '''
    name = 'company_info'

    start_urls = [
        'https://emops.twse.com.tw/server-java/t51sb01_e',
    ]

    def start_requests(self):
        form_data = {
            'step': '0', 'caption_id': '000001',
            'page': '', 'TYPE': '', 'TYPEK': '',
        }
        for url in self.start_urls:
            yield FormRequest(
                url, callback=self.parse,
                method='POST', formdata=form_data
            )

    def value_processor(self, value: str) -> str:
        REPLACE_MAP = {
            '¡Ð': '',
        }
        replace_value = REPLACE_MAP.get(value, None)
        if replace_value is None:
            replace_value = value
        return replace_value

    def parse(self, response, **kwargs) -> Generator:
        COLUMN_NAMES_IDX = 0
        field_names = [
            'market', 'company_id', 'company_name',
            'place_of_incorporation_of_foreign_companies',
            'industry', 'symbol', 'date_of_listing',
            'chariman', 'general_manager', 'spokesman',
            'title_of_spokersman', 'fiscal_year_end',
            'accounting_firm', 'cpa_1', 'cpa_2',
            'address', 'telephone', 'fax','email',
            'web_address', 'investor_relations_contact_person',
            'title_of_ir_contact_person', 'telephon_of_ir_contact_person',
            'email_of_ir_contact_person',
        ]
        table_rows = response.xpath('.//table[2]//tr')
        for idx, row in enumerate(table_rows):
            if idx == COLUMN_NAMES_IDX:
                continue
            company_info_item = CompanyInfoItem()
            column_values = row.css('td')
            for field_name, value_tag in zip(field_names, column_values):
                value = value_tag.css('td::text').get()
                value = self.value_processor(value)
                # Populating the data to item
                company_info_item[field_name] = value
            yield company_info_item
            
        
            
            
                

            
