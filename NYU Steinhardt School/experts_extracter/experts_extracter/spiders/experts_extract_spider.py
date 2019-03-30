# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem




class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["steinhardt.nyu.edu"]
    start_urls = ['https://steinhardt.nyu.edu/about/faculty_experts']

    def parse(self, response):
        expertise_map = self.get_expertise_map(response)
        experts = response.xpath('//main[@id="main"]//li/a')
        for expert in experts:
            item = ExpertsExtractItem()    
            
            name = expert.xpath('text()').extract_first()
            link = expert.xpath('@href').extract_first()
            if 'https://steinhardt.nyu.edu/' not in link:
                link = 'https://steinhardt.nyu.edu' + link
            
            item['name'] = name
            item['faculty_page'] = link
            
            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            expertise_in_main_page = [expertise for expertise,experts in expertise_map.iteritems() if name in experts]
            if expertise_in_main_page:
                request.meta['expertise_in_main_page'] = expertise_in_main_page
            request.meta['item'] = item
            yield request
            
    def parse_each_expert(self, response):
        item = response.meta['item']
        expertise_in_main_page = response.meta['expertise_in_main_page']
    
        title = response.xpath('//div[@id="bio_component"]/h4/text()').extract_first()
        if title:
            item['title'] = title.strip()
        
        phone = response.xpath('//p[contains(@class,"contact_info")]/span[@class="tel"]/text()').extract_first()
        if phone:
            item['phone'] = phone.strip()

        email = response.xpath('//p[contains(@class,"contact_info")]/a[@class="uid email"]/text()').extract_first()
        if email:
            item['email'] = email.strip()
        
        department_block = response.xpath("//li[contains(text(), 'Department')]/following-sibling::ul[1]/li/span/a/text()").extract()
        if department_block:
            for i, value in enumerate(department_block):
                item['department_%s' % (i+1)] = value.strip()

        headshot = response.xpath('//img[@id="the_photo"]/@src').extract_first()
        if headshot:
            item['headshot'] = 'https://steinhardt.nyu.edu' + headshot
        
        biography =  response.xpath('//p[@class="bio_bio summary"]/following-sibling::*')
        if biography:
            item['biography'] = ' '.join(line.strip('\n') for line in biography.xpath('string()').extract() if line.strip('\n'))
        
        for i, value in enumerate(expertise_in_main_page, 1):
            item['areas_of_expertise_%s' % i] = value

        expertise_section = response.xpath('//div[@id="researchModule"]/ul/li/text()').extract()
        if expertise_section:
            expertise = [re.split(r',|;', e) for e in expertise_section][0]
            for j, value in enumerate(expertise, i+1):
                item['areas_of_expertise_%s' % j] = value
        yield item


    def get_expertise_map(self, response):
        main = response.xpath('//main[@id="main"]//h5')
        expertise_map = dict()
        for category in main:
            
            sub_categories = category.xpath('following-sibling::ul[1]//li[text() or @class="expertSubCategory"]')
            if sub_categories:
                for c in sub_categories:
                    sub_category = c.xpath('text()').extract_first()
                    if sub_category:
                        if c.xpath('ul'):
                            experts = c.xpath('ul//a/text()').extract()
                            if experts:
                                expertise_map.update({sub_category.strip('\n'):experts})
                                # print sub_category.strip('\n'), experts
                                # print '\n'
                        else:
                            experts = c.xpath('following-sibling::ul[1]//a/text()').extract()
                            if experts:
                                expertise_map.update({sub_category.strip('\n'):experts})
                                # print sub_category.strip('\n'), experts
                                # print '\n'

            else:
                experts = category.xpath('following-sibling::ul[1]//a/text()').extract()
                if experts:
                    category = category.xpath('text()').extract_first()
                    expertise_map.update({category.strip('\n'):experts})
                    # print category.strip('\n'), experts
                    # print '\n'
        return expertise_map