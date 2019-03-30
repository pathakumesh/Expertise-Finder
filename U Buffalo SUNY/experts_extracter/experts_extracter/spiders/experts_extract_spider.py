# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem

class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["buffalo.edu"]
    start_urls = ['http://www.buffalo.edu/news/faculty-experts/a-z.html']

    def parse(self, response):
        
        experts = response.xpath('//div[@class="teaser-image"]')
        for expert in experts:
            link = expert.xpath('a/@href').extract_first()
            if 'http://www.buffalo.edu' not in link:
                link = 'http://www.buffalo.edu' + link

            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            yield request
        

            
    def parse_each_expert(self, response):
        item = ExpertsExtractItem()
        
        name = response.xpath('//div[@class="title section"]/h1[@id="title_1" or @id="title"]/text()').extract_first()
        if name:
            item['name'] = name.strip()
        
        title_block= response.xpath('//div[@class="title section"]/h1[@id="title_1" or @id="title"]/../following-sibling::div[1][@class="introtext text parbase section"]/p')
        if not title_block:
            title_block= response.xpath('//div[@class="title section"]/h1[@id="title_1" or @id="title"]/../following-sibling::div[2][@class="introtext text parbase section"]/p')
        title =  title_block.xpath('text()').extract_first()
        if title:
            item['title'] = title.strip()
        
        college = title_block.xpath('i/text()').extract_first()
        if college:
            item['college'] = college.strip()

        areas_of_expertise_block = response.xpath('//h3[contains(text(),"AREAS OF EXPERTISE")]/../following-sibling::div[1]/p')
        if areas_of_expertise_block:
            areas_of_expertise = areas_of_expertise_block.xpath('string()').extract_first().split(',')
            for i, expertise in enumerate(areas_of_expertise, 1):
                item['areas_of_expertise_%s' % i] = expertise
        
        headshot = response.xpath('//div[contains(@class, "image-container")]//img/@src').extract_first()
        if headshot:
            item['headshot'] = 'http://www.buffalo.edu' + headshot
        
        
        bio_block = response.xpath('//div[contains(@class, "image-container")]/following-sibling::div[1][@class="text parbase section"]')
        if bio_block:
            item['biography'] = bio_block.xpath('string()').extract()[0]
        
        
        contact_block= response.xpath('//div[@class="text parbase section"]/ul/li')
        if len(contact_block) >= 3:
            item['phone'] =  contact_block[0].xpath('text()').extract_first()
            item['email'] =  contact_block[1].xpath('a/text()').extract_first()
            item['personal_site'] = contact_block[2].xpath('a/@href').extract_first()

        elif contact_block[-1].xpath('a[contains(text(), "website")]'):
            item['phone'],item['email'] =  contact_block[0].xpath('string()').re(r'.*?(\d+-\d+-\d+).*?(\S+@\S+)')
            item['personal_site'] =  contact_block[1].xpath('a/@href').extract_first()
        elif len(contact_block[0].xpath('string()').re(r'.*?(\d+-\d+-\d+).*?(\S+@\S+)')) == 2:
            item['phone'],item['email'] =  contact_block[0].xpath('string()').re(r'.*?(\d+-\d+-\d+).*?(\S+@\S+)')

        else:
            item['phone'] =  contact_block[0].xpath('text()').extract_first()
            item['email'] =  contact_block[1].xpath('a/text()').extract_first()

        item['faculty_page'] = response.url
         
        yield item
