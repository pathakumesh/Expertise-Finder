# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem


class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["umass.edu"]
    start_urls = ['http://www.umass.edu/newsoffice/resources']

    def parse(self, response):
        print 'next_page_url ', response.url
        experts = response.xpath('//div[@class="view-content"]/div')
        print len(experts)
        for expert in experts:
            link = "http://www.umass.edu" + expert.xpath('div[@class="views-field views-field-field-photo"]//a/@href').extract_first()
            
            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            
            # request.meta['dont_redirect'] = True
            # request.meta['handle_httpstatus_all'] = True
            yield request

        # If next page is there, make a request and proceed similar as above.
        next_page = response.xpath('//a[contains(@title,"next page")]')
        if next_page:
            next_page_url = "http://www.umass.edu" + next_page.xpath('@href').extract_first()
            yield scrapy.Request(next_page_url, callback=self.parse)
            
    def parse_each_expert(self, response):
        item = ExpertsExtractItem()
        item['faculty_page'] = response.url

        name = response.xpath('//header[@id="main-content-header"]/h1/text()').extract_first()
        if name:
            item['name'] = name.strip()
        
        article_block = response.xpath('//article[contains(@class, "node-expert")]/div[@class="content"]')
        
        title_block = article_block.xpath('h3/text()').extract_first()
        for i,title in enumerate(title_block.split(','), 1):
            item['title_%s' % i] = title.strip()
        
        headshot = article_block.xpath('img/@src').extract_first()
        if headshot:
            item['headshot'] = headshot

        areas_of_expertise = article_block.xpath('h2/text()').extract_first()
        for i, expertise in enumerate(areas_of_expertise.split(','), 1):
            item['areas_of_expertise_%s' % i] = expertise

        phone = article_block.xpath('p/b[contains(text(), "Phone")]/../text()').extract_first()
        if phone:
            item['phone'] = phone.strip()
        email = article_block.xpath('b[contains(text(), "Email")]/following-sibling::a[1]/text()').extract_first()
        if email:
            item['email'] = email.strip()
        
        if not email:
            biography = article_block.xpath('p//text()').extract()
        else:
            biography = article_block.xpath('b[contains(text(), "Email")]/following-sibling::p//text()').extract()
            if not biography:
                biography = article_block.xpath('b[contains(text(), "Email")]/following-sibling::div//text()').extract()

        if biography:
            item['biography'] = ''.join(bio.replace('\n', '').replace('\t', '').replace('\r', '') for bio in biography)

        yield item