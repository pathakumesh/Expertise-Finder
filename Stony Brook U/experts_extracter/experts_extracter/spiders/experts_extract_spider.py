# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem


class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["stonybrook.edu"]
    start_urls = ['https://www.stonybrook.edu/experts/results/']

    def parse(self, response):
        experts = response.xpath('//div[contains(@class,"faculty-list")]/table//tr')
        for expert in experts[1:]:
            item = ExpertsExtractItem()
            row_data = expert.xpath('td')
            name = row_data[0].xpath('a/text()').extract_first()
            if name:
                item['name'] = name.strip()
            
            link = row_data[0].xpath('a/@href').extract_first()
            link = "https://www.stonybrook.edu/" + link if 'https:' not in link else link

            department = row_data[1].xpath('text()').extract_first()
            if department:
                item['department'] = department        
            
            expertise_block = row_data[2].xpath('a/text()').extract()
            if expertise_block:
                for i, ex in enumerate(expertise_block,1):
                    item['areas_of_expertise_%s' % i] = ex.strip()

            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            request.meta['item'] = item
            yield request

            
    def parse_each_expert(self, response):
        item = response.meta['item']
        item['faculty_page'] = response.url

        title_block = response.xpath('//span[contains(@class,"summary-1")]/text()').extract()
        for i, title in enumerate(title_block , 1):
            title = title.replace('\n', '')
            item['title_%s' % i] = re.sub(r'\s{2,}', ' ', title).strip()

        website = response.xpath('//a[contains(string(), "Website")]/@href').extract_first()
        if website:
            item['website'] = website.strip()


        bio_block =  response.xpath('//div[@class="bio"]')
        if bio_block:
            bio =  bio_block.xpath('string()').extract_first()
            item['biography'] = re.sub(r'\s{2,}', ' ', bio).strip()

        headshot = response.xpath('//div[@class="left-col"]/img/@src').extract_first()
        if headshot:
            item['headshot'] = "https://www.stonybrook.edu" + headshot if "https://www.stonybrook.edu/" not in headshot else headshot

        yield item
