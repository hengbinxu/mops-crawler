from functools import wraps
from typing import Callable

from scrapy import Item, Spider


def check_spider_pipeline(process_item_method: Callable) -> Callable:
    '''
    Check which pipeline will be invoked by the spider.
    If the spider doesn't define the attribute `pipeline`,
    it will invoke all pipelines that have been written on `settings.py`. 
    '''
    @wraps(process_item_method)
    def wrapper(self, item: Item, spider: Spider) -> Callable:

        msg = '{} pipeline '.format(self.__class__.__name__)

        if self.__class__.__name__ in spider.pipeline or\
            not hasattr(spider, 'pipeline'):
            spider.logger.info(msg + 'executing...')
            return process_item_method(self, item, spider)
        else:
            spider.logger.info(msg + 'skipping...')
            return item
    return wrapper


# How to use different pipeline for different spider in Scrapy single project?
# https://stackoverflow.com/questions/8372703/how-can-i-use-different-pipelines-for-different-spiders-in-a-single-scrapy-project