# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem

class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["news.syr.edu"]
    start_urls = ['https://news.syr.edu/faculty-experts/']

    def parse(self, response):
        
        experts = response.xpath('//h3[@class="article-title"]')
        for expert in experts:
            link = expert.xpath('a/@href').extract_first()

            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            yield request
        

            
    def parse_each_expert(self, response):
        item = ExpertsExtractItem()
        
        name = response.xpath('//div/h1[@class="article-title"]/text()').extract_first()
        if name:
            item['name'] = name.strip()
        
        title = response.xpath('//div/div[@class="title"]/text()').extract_first()
        if title:
            item['title'] = title.strip()
        
        phone = response.xpath('//ul[@class="contact-info"]/li/a[@class="icon phone"]/text()').extract_first()
        if phone:
            item['phone'] = phone.strip()

        email = response.xpath('//ul[@class="contact-info"]/li/a[@class="icon email"]/text()').extract_first()
        if email:
            item['email'] = email.strip()

        twitter = response.xpath('//ul[@class="contact-info"]/li/a[@class="icon twitter"]/text()').extract_first()
        if twitter:
            item['twitter'] = twitter.strip()

        personal_site = response.xpath('//ul[@class="contact-info"]/li/a[@class="icon website"]/@href').extract_first()
        if personal_site:
            item['personal_site'] = personal_site.strip()

        
        bio_block = response.xpath('//div[@class="bio"]')
        if bio_block:
            item['biography'] = " ".join(b.strip() for b in bio_block.xpath('string()').extract())
        
        if bio_block:
            areas_of_expertise = response.xpath('//div[@class="bio"]/preceding-sibling::div[1]/ul/li/a/text()').extract()
        else:
            areas_of_expertise = response.xpath('//div[@class="link-to-bio"]/preceding-sibling::div[1]/ul/li/a/text()').extract()
        
        for i, expertise in enumerate(areas_of_expertise, 1):
            item['areas_of_expertise_%s' % i] = expertise


        faculty_page = response.xpath('//div[@class="link-to-bio"]/a/@href').extract_first()
        if faculty_page:
            item['faculty_page'] = faculty_page
        
        item['page_link'] = response.url

        
        
        
        headshot = response.xpath('//div[contains(@style, "background-image:url")]/@style').re(r'.*?url\((.*?)\)')
        if headshot:
            item['headshot'] = headshot[0]
         
        yield item
