# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem

class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["dental.nyu.edu"]
    start_urls = ['https://dental.nyu.edu/aboutus/news/faculty-experts.html']

    def parse(self, response):
        
        experts = response.xpath('//div[contains(@id, "aquadBoxnyuexpandables") and @class="answer"]/p[strong or a]')
        for expert in experts:
            item = ExpertsExtractItem()
            link = None
            if expert.xpath('strong/a'):
                name = expert.xpath('strong/a/text()').extract_first()
                link = expert.xpath('strong/a/@href').extract_first()
            
            elif expert.xpath('strong'):
                name = expert.xpath('strong/text()').extract_first()

            else:
                name = expert.xpath('a/strong/text()').extract_first()
                link = expert.xpath('a/@href').extract_first()
            
            if link and 'https://dental.nyu.edu' not in link:
                link = 'https://dental.nyu.edu' + link
            
            item['name'] = name.split(',')[0]
            
            bio_block =  expert.xpath('following-sibling::ul[1]/li')
            areas_of_expertise, biography =  bio_block.xpath('string()').extract()
            
            areas_of_expertise = areas_of_expertise.split('EXPERTISE:')[-1]
            biography = biography.split('BACKGROUND:')[-1]

            for i, expertise in enumerate(areas_of_expertise.split(';'), 1):
                item['areas_of_expertise_%s' % i] = expertise.strip()
            item['biography'] = biography.strip()
            
            if link:
                # Make a request to actual link for the blog to extract other info
                request =  scrapy.Request(link, callback=self.parse_each_expert)
                request.meta['item'] = item
                yield request
            else:
                yield item
        

            
    def parse_each_expert(self, response):
        item = response.meta['item']
        item['faculty_page'] = response.url
        if not response.status == 404:
            contact_block= response.xpath('//h4[contains(text(),"Education")\
                                    or contains(text(),"EDUCATION")\
                                    or contains(text(),"HONORS")\
                                    or contains(text(),"REPRESENTATIVE")\
                                    or contains(text(),"RESEARCH INTERESTS")]/preceding-sibling::p/text()').extract()
            if not contact_block:
                contact_block= response.xpath('//div[@class="span-3"]//h3/following-sibling::p/text()').extract()

            title_block = list()
            for i in contact_block:
                if any(x in i for x in ['Phone','Fax', 'E-mail']):
                    break
                title_block.append(i)

            department  = title_block[-2]
            item['department'] = department
            
            for i, expertise in enumerate(title_block[0:-2], 1):
                item['title_%s' % i] = expertise.strip()

            phone = [x for x in contact_block if 'Phone' in x]
            if phone:
                item['phone'] = phone[0].split('Phone:')[-1].strip()

            email = response.xpath('//div[@class="span-3"]//a[contains(@href, "mailto")]/strong/text()').extract_first()
            if email:
                item['email'] = email


            headshot = response.xpath('//div[@class="span-1"]//img/@src').extract_first()
            if headshot:
                item['headshot'] = headshot

        yield item
