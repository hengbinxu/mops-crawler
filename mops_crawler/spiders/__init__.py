# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import re, os

from scrapy import Spider
from scrapy import Request

from ..request_info import MopsRequestInfo, AFTER_IFRS_YEARS
from ..company_list import CompanyList
from ..settings import ENV

class MopsSpider(Spider):
    
    name = None

    # Define data clean functions
    def to_lowercase(self, value: str) -> str:
        return value.lower()

    def remove_space(self, value: str) -> str:
        return value.strip()

    def replace_symbol(self, value: str) -> str:
        return value.replace('-', '_')

    def replace_space(self, value: str) -> str:
        return value.replace(' ', '_')

    def remove_comma(self, value: str) -> str:
        return value.replace(',', '')

    def process_unit(self, value: str) -> str:
        replace_pat = re.compile(r'Unit:\s')
        value = replace_pat.sub('', value)
        return value.replace(' ', ',')

    def remove_parentheses(self, value: str) -> str:
        replace_pat = re.compile('[\(|\)]')
        value = replace_pat.sub('', value)
        return value

    def value_processor(self, value: str) -> str:
        '''
        Data clear function to clean values.
        '''
        process_funcs = [
            self.remove_space,
            self.remove_comma,
        ]
        for func in process_funcs:
            value = func(value)
        return value

    @property
    def start_urls(self):
        for company_info in CompanyList.get_company_list():
            company_id = company_info['company_id']
            for year in AFTER_IFRS_YEARS:
                mops_request_info = MopsRequestInfo(self.name, company_id, year)
                yield mops_request_info.request_info

    def start_requests(self):
        for idx, url_info in enumerate(self.start_urls):
            url = url_info['request_url']
            method = url_info['method']
            query_parameters = url_info['query_parameters']
            yield Request(
                url, callback=self.parse,
                method=method, cb_kwargs=query_parameters
            )
            if ENV == 'dev':
                if idx > 1:
                    break