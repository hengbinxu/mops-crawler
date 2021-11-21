# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class IncomeStatementPipeline:
    def process_item(self, item, spider):
        return item



# How to use different pipeline for different spider in Scrapy single project?
# https://stackoverflow.com/questions/8372703/how-can-i-use-different-pipelines-for-different-spiders-in-a-single-scrapy-proje