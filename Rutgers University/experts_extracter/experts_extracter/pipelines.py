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
        self.file_name = 'Rutgers University.csv'
        self.export_fields = ["name","title","department", "school_college", "campus", "other", "biography", "email",
        "phone","extension","faculty_page", "headshot","personal_site",
        "key_topics_1","key_topics_2","key_topics_3","key_topics_4",
        "key_topics_5","key_topics_6","key_topics_7","key_topics_8",
        "key_topics_9","key_topics_10","key_topics_11","key_topics_12",
        "key_topics_13","key_topics_14","key_topics_15","key_topics_16","key_topics_17",
        "key_topics_18","key_topics_19","key_topics_20"
        ]

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
