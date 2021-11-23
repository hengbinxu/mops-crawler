# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os, pathlib

from typing import Generator

from scrapy import Spider, Item
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.exporters import CsvItemExporter
from itemadapter import ItemAdapter


class CsvExportPipeline:

    FILE_EXTENSION = 'csv'

    def __init__(self, reports_output_dir):
        self.reports_output_dir = reports_output_dir

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            reports_output_dir=crawler.settings.get('REPORTS_OUTPUT_DIR')
        )

    def open_spider(self, spider: Spider):
        # mkdir file directory and get file name
        pathlib.Path(self.reports_output_dir).mkdir(parents=True, exist_ok=True)
        file_name = '{}.{}'.format(spider.name, self.FILE_EXTENSION)
        output_file_path = os.path.join(self.reports_output_dir, file_name)
        # Open the file and instantiate CsvItemExporter
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
    '''
    The data pipeline is used for exporting multiple csv files by each request.
    But it needs to notice that IOError: Too many open files, all of the requests can be 
    separated into mini batch. The default file descriptors of MacOS is 256, it can be 
    modified by ulimit command.
    '''
    FILE_EXTENSION = 'csv'

    def __init__(self, output_dir: str, crawler_obj: Crawler):
        self.output_dir = output_dir
        self.crawler_obj = crawler_obj
        self.save_folder_path = os.path.join(self.output_dir, self.crawler_obj.spider.name)
        # Initial export data container
        self.exporter_container = dict()
        self.crawler_obj.signals.connect(self.open_spider, signal=signals.spider_opened)
        self.crawler_obj.signals.connect(self.close_spidr, signal=signals.spider_closed)      

    def get_file_name(self, company_id: str, year: str) -> str:
        file_name = '{company_id}-{year}.{file_extension}'.format(
            company_id=company_id,
            year=year,
            file_extension=self.FILE_EXTENSION
        )
        return file_name
    
    def generate_file_path(self, spider: Spider) -> Generator:
        for request_info in spider.start_urls:
            query_parameters = request_info['query_parameters']
            company_id = query_parameters['co_id']
            year = query_parameters['year']
            file_name = self.get_file_name(company_id, year)
            yield os.path.join(self.save_folder_path, file_name)
    
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            output_dir=crawler.settings.get('REPORTS_OUTPUT_DIR'),
            crawler_obj=crawler
        )
    
    def open_spider(self, spider: Spider):
        # Ensure the directory exsits       
        pathlib.Path(self.save_folder_path).mkdir(parents=True, exist_ok=True)
        for output_file_path in self.generate_file_path(spider):
            # Place exporter to specific data container 
            f = open(output_file_path, 'wb')
            self.exporter_container[output_file_path] = {
                'file': f,
                'exporter': CsvItemExporter(f, encoding='utf-8'),
            }
            self.exporter_container[output_file_path]['exporter'].start_exporting()

        first_container_obj = list(self.exporter_container.items())[0]
        spider.logger.info('{} call open_spider function...'.format(self.__class__.__name__))
        spider.logger.info('The first export_files_container: {}'.format(first_container_obj))
        spider.logger.info('The length of export_files_container: {}'.format(len(self.exporter_container)))

    def process_item(self, item: Item, spider: Spider) -> Item:
        item_adapter = ItemAdapter(item)
        company_id = item_adapter.get('company_id')
        year = item_adapter.get('year')
        file_name = self.get_file_name(company_id, year)
        output_file_path = os.path.join(self.save_folder_path, file_name)
        # Use output_file_path to find specified Export item
        self.exporter_container[output_file_path]['exporter'].export_item(item)
        return item

    def close_spidr(self, spider: Spider):
        for output_file_path in self.generate_file_path(spider):
            self.exporter_container[output_file_path]['exporter'].finish_exporting()
            self.exporter_container[output_file_path]['file'].close()

        spider.logger.info('{} call close_spider function...'.format(self.__class__.__name__))


# How to use different pipeline for different spider in Scrapy single project?
# https://stackoverflow.com/questions/8372703/how-can-i-use-different-pipelines-for-different-spiders-in-a-single-scrapy-project

# export-scrapy-items-to-different-files
# https://stackoverflow.com/questions/50083638/export-scrapy-items-to-different-files