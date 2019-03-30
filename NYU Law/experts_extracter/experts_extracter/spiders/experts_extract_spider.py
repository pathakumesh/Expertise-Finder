# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem




class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["law.nyu.edu"]
    start_urls = ['https://its.law.nyu.edu/mediaGuide']

    def parse(self, response):
        expert_areas = response.xpath('//div[@id="content"]//li/a')
        for area in expert_areas:
            link = area.xpath('@href').extract_first()
            if 'https://its.law.nyu.edu/mediaGuide' not in link:
                link = 'https://its.law.nyu.edu/mediaGuide/' + link
            
            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expertise)
            yield request
            
    def parse_each_expertise(self, response):
        experts = response.xpath('//div[@id="content"]//li/a')
        for expert in experts:
            link = expert.xpath('@href').extract_first()
            if 'https://its.law.nyu.edu' not in link:
                link = 'https://its.law.nyu.edu' + link
            
            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            yield request
    
    def parse_each_expert(self, response):
        item = ExpertsExtractItem()
        item['faculty_page'] = response.url

        name = response.xpath('//div[@id="faculty-info"]/h1/text()').extract_first()
        if name:
            item['name'] = name

        title = response.xpath('//div[@id="faculty-info"]/ul/li')
        if title:
            for i, value in enumerate(title, 1):
                item['title_%s' % i] = value.xpath('text()').extract_first().strip()
        
        phone = response.xpath('//div[@id="facluty-contact"]//a[contains(@href, "tel:")]/text()').extract_first()
        if phone:
            item['phone'] = phone.strip()

        email = response.xpath('//div[@id="facluty-contact"]//a[contains(@href, "mailto:")]/text()').extract_first()
        if email:
            item['email'] = email.strip()

        headshot = response.xpath('//div[@class="region-photo"]//img/@src').extract_first()
        if headshot:
            item['headshot'] = 'https://its.law.nyu.edu' + headshot
        
        biography =  response.xpath('//div[@id="full-bio-text"]/p/text()').extract_first()
        if biography:
            item['biography'] = biography
        
        expertise_block = response.xpath('//p[@id="expertise-text"]/text()').extract_first()
        if expertise_block:
            for i, value in enumerate(expertise_block.split(','), 1):
                item['areas_of_expertise_%s' % i] = value

        yield item

