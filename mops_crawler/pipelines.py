# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os, pathlib
from scrapy import Spider, Item
from scrapy import signals
from scrapy.crawler import Crawler

from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter


class CsvExportPipeline:

    FILE_EXTENSION = '.csv'

    def __init__(self, reports_output_dir):
        self.reports_output_dir = reports_output_dir

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            reports_output_dir=crawler.settings.get('REPORTS_OUTPUT_DIR')
        )

    def open_spider(self, spider: Spider):
        file_name = spider.name + self.FILE_EXTENSION
        pathlib.Path(self.reports_output_dir).mkdir(parents=True, exist_ok=True)
        output_file_path = os.path.join(self.reports_output_dir, file_name)
        self.file = open(output_file_path, 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    def process_item(self, item: Item, spider: Spider) -> Item:
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider: Spider):
        self.exporter.finish_exporting()
        self.file.close()


class MultiExportPipeline():

    FILE_EXTENSION = '.csv'

    def __init__(self, output_dir: str, crawler_obj: Crawler):
        self.output_dir = output_dir
        self.crawler_obj = crawler_obj
        self.exporter_container = dict()
        crawler_obj.signals.connect(self.open_spider, signal=signals.spider_opened)
        crawler_obj.signals.connect(self.close_spidr, signal=signals.spider_closed)
    
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            output_dir=crawler.settings.get('REPORTS_OUTPUT_DIR'),
            crawler_obj=crawler
        )
    
    def open_spider(self, spider: Spider):
        self.save_folder_path = os.path.join(self.output_dir, spider.name)        
        pathlib.Path(self.save_folder_path).mkdir(parents=True, exist_ok=True)
        
        for request_info in spider.start_urls:
            query_parameters = request_info['query_parameters']
            company_id = query_parameters['co_id']
            year = query_parameters['year']
            file_name = '{}-{}{}'.format(company_id, year, self.FILE_EXTENSION)
            output_file_path = os.path.join(self.save_folder_path, file_name)

            # Put exporter to specific data container 
            f = open(output_file_path, 'wb')
            self.exporter_container[output_file_path] = {
                'file': f,
                'exporter': CsvItemExporter(f, encoding='utf-8'),
            }
            self.exporter_container[output_file_path]['exporter'].start_exporting()

        print('export_files_container: {}'.format(self.exporter_container))

    def process_item(self, item: Item, spider: Spider) -> Item:
        item_adapter = ItemAdapter(item)
        company_id = item_adapter.get('company_id')
        year = item_adapter.get('year')
        file_name = '{}-{}{}'.format(company_id, year, self.FILE_EXTENSION)
        output_file_path = os.path.join(self.save_folder_path, file_name)
        # Use output_file_path to find specified Export item
        self.exporter_container[output_file_path]['exporter'].export_item(item)
        return item

    def close_spidr(self, spider: Spider):
        for request_info in spider.start_urls:
            query_parameters = request_info['query_parameters']
            company_id = query_parameters['co_id']
            year = query_parameters['year']
            file_name = '{}-{}{}'.format(company_id, year, self.FILE_EXTENSION)
            output_file_path = os.path.join(self.save_folder_path, file_name)

            self.exporter_container[output_file_path]['exporter'].finish_exporting()
            self.exporter_container[output_file_path]['file'].close()

# How to use different pipeline for different spider in Scrapy single project?
# https://stackoverflow.com/questions/8372703/how-can-i-use-different-pipelines-for-different-spiders-in-a-single-scrapy-project

# export-scrapy-items-to-different-files
# https://stackoverflow.com/questions/50083638/export-scrapy-items-to-different-files