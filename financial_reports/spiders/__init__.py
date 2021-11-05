# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from scrapy import Spider
from scrapy import Request

from ..request_info import MopsRequestInfo
from ..company_list import CompanyList

class MopsSpider(Spider):
    
    name = None

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
        ),
        'Accept': (
            'text/html,application/xhtml+xml,'
            'application/xml;q=0.9,image/avif,image/webp,'
            'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        ),
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        'Host': 'emops.twse.com.tw',
    }
    
    # TODO:
    # Need to add year
    @property
    def start_urls(self):
        for company_info in CompanyList.get_company_list():
            company_id = company_info['company_id']
            mops_request_info = MopsRequestInfo(self.name, company_id, 2020)
            yield mops_request_info.request_info

    def start_requests(self):
        for url_info in self.start_urls:
            url = url_info['request_url']
            method = url_info['method']
            print(url_info)
            input('-' * 100)
            yield Request(url, callback=self.parse, method=method, headers=self.headers)
            