# -*- coding: utf-8 -*-
import os
import csv
from scrapy import signals
from scrapy.exporters import CsvItemExporter
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ExpertsExtractPipeline(object):
    def __init__(self):
        self.files = {}
        self.file_name = 'NYU Steinhardt School.csv'
        self.export_fields = ["name","title","phone","email","department_1",
        "department_2","biography","headshot","faculty_page",
        "areas_of_expertise_1","areas_of_expertise_2","areas_of_expertise_3","areas_of_expertise_4",
        "areas_of_expertise_5","areas_of_expertise_6","areas_of_expertise_7","areas_of_expertise_8",
        "areas_of_expertise_9","areas_of_expertise_10","areas_of_expertise_11","areas_of_expertise_12",
        "areas_of_expertise_13"]

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        
        output_file = open(self.file_name, 'w+b')
        self.files[spider] = output_file
        self.exporter = CsvItemExporter(output_file,fields_to_export = self.export_fields)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        output_file = self.files.pop(spider)
        output_file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
