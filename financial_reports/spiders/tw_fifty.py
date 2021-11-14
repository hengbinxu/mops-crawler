import json

from scrapy import Spider
from scrapy.http import FormRequest, Response

from ..items import TWFiftyItem

class TWFifty(Spider):
    
    name = 'tw_fifty'

    @property
    def start_urls(self):
        url = ["https://www.cmoney.tw/etf/ashx/e210.ashx",]
        return url

    def start_requests(self):
        form_data = {
            'action': 'GetShareholdingDetails',
            'stockId': '0050',
        }
        for url in self.start_urls:
            yield FormRequest(
                url, callback=self.parse,
                method='POST', formdata=form_data
            )

    def parse(self, response: Response, **kwargs):
        response_data = json.loads(response.body.decode())
        all_company_data = response_data['Data']
        for company_data in all_company_data:
            tw_fifty_item = TWFiftyItem()
            tw_fifty_item['company_id'] = company_data['CommKey']
            tw_fifty_item['company_name'] = company_data['CommName']
            tw_fifty_item['weight'] = company_data['Weights']
            yield tw_fifty_item