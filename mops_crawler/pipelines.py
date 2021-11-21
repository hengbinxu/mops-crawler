# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os, pathlib

from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter


class CsvExportPipeline:

    FILE_EXTENSION = '.csv'

    def __init__(self, reports_output_dir):
        self.reports_output_dir = reports_output_dir

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            reports_output_dir=crawler.settings.get('REPORTS_OUTPUT_DIR')
        )

    def open_spider(self, spider):
        file_name = spider.name + self.FILE_EXTENSION
        pathlib.Path(self.reports_output_dir).mkdir(parents=True, exist_ok=True)
        output_file_path = os.path.join(self.reports_output_dir, file_name)
        self.file = open(output_file_path, 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


# How to use different pipeline for different spider in Scrapy single project?
# https://stackoverflow.com/questions/8372703/how-can-i-use-different-pipelines-for-different-spiders-in-a-single-scrapy-project

# export-scrapy-items-to-different-files
# https://stackoverflow.com/questions/50083638/export-scrapy-items-to-different-files