# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os, pathlib

from scrapy import Spider, Item
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.exporters import CsvItemExporter
from itemadapter import ItemAdapter

from .utils import check_spider_pipeline


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
        pass

    @check_spider_pipeline
    def process_item(self, item: Item, spider: Spider) -> Item:
        # mkdir file directory and get file name
        pathlib.Path(self.reports_output_dir).mkdir(parents=True, exist_ok=True)
        file_name = '{}.{}'.format(spider.name, self.FILE_EXTENSION)
        output_file_path = os.path.join(self.reports_output_dir, file_name)
        
        # Open the file and instantiate CsvItemExporter
        if not hasattr(self, 'file'):
            self.file = open(output_file_path, 'wb')
            self.exporter = CsvItemExporter(self.file, encoding='utf-8')
            self.exporter.start_exporting()
        
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider: Spider):
        self.exporter.finish_exporting()
        self.file.close()

        spider.logger.info((
            '{} successfully close file and exporter.'
        ).format(self.__class__.__name__))


class MultiExportPipeline():
    '''
    The data pipeline is used for exporting multiple csv files by each request.
    But it needs to notice that IOError: Too many open files, all of the requests can be 
    separated into mini batch to avoid the error. The default file descriptors of MacOS is 256,
    it can be modified by ulimit command.
    '''
    FILE_EXTENSION = 'csv'

    def __init__(self, output_dir: str, crawler_obj: Crawler):
        self.output_dir = output_dir
        self.crawler_obj = crawler_obj
        self.save_folder_path = os.path.join(self.output_dir, self.crawler_obj.spider.name)
        # Initial export data container
        self.exporter_container = dict()
        self.crawler_obj.signals.connect(self.open_spider, signal=signals.spider_opened)
        self.crawler_obj.signals.connect(self.close_spider, signal=signals.spider_closed)      

    def get_file_name(self, company_id: str, year: str) -> str:
        file_name = '{company_id}-{year}.{file_extension}'.format(
            company_id=company_id,
            year=year,
            file_extension=self.FILE_EXTENSION
        )
        return file_name
    
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            output_dir=crawler.settings.get('REPORTS_OUTPUT_DIR'),
            crawler_obj=crawler
        )
    
    def open_spider(self, spider: Spider):
        spider.logger.info('{} call open_spider function...'.format(self.__class__.__name__))
        pass

    @check_spider_pipeline
    def process_item(self, item: Item, spider: Spider) -> Item:
        # Ensure the directory exsits 
        path = pathlib.Path(self.save_folder_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        item_adapter = ItemAdapter(item)
        company_id = item_adapter.get('company_id')
        year = item_adapter.get('year')
        file_name = self.get_file_name(company_id, year)
        output_file_path = os.path.join(self.save_folder_path, file_name)
        try:
            # Use output_file_path to find specified export object
            exporter = self.exporter_container[output_file_path]['exporter']
            exporter.export_item(item)
        except KeyError:
            f = open(output_file_path, 'wb')
            exporter = CsvItemExporter(f)
            exporter.start_exporting()
            exporter.export_item(item)
            self.exporter_container[output_file_path] = {'file': f, 'exporter': exporter}
        return item

    def close_spider(self, spider: Spider):
        spider.logger.info('{} call close_spider function...'.format(self.__class__.__name__))
        for files_object in self.exporter_container.values():
            files_object['exporter'].finish_exporting()
            files_object['file'].close()
        
        spider.logger.info((
            '{} successfully close all files and exporters.'
        ).format(self.__class__.__name__))


# export-scrapy-items-to-different-files
# https://stackoverflow.com/questions/50083638/export-scrapy-items-to-different-files