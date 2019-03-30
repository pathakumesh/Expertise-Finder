# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem
from selenium import webdriver


class ExpertsExtractSpider(scrapy.Spider):
    chromedriver = "/Users/PathakUmesh/Downloads/SeleniumWorks/chromedriver"
    browser = webdriver.Chrome(chromedriver)
    name = "expert_extract_spider"
    allowed_domains = ["williams.edu"]
    start_urls = ['https://communications.williams.edu/media-relations/faculty-experts/']

    
    def parse(self, response):
        tags = response.xpath('//div[@id="faculty-experts-tagcloud"]/a')
        for tag in tags:
            link = tag.xpath('@href').extract_first()
            request =  scrapy.Request(link, callback=self.parse_each_tag)
            yield request

    def parse_each_tag(self, response):
        names = response.xpath('//h2[@class="post-title"]/a')
        for name in names:
            link = name.xpath('@href').extract_first()
            request =  scrapy.Request(link, callback=self.parse_each_name)
            yield request

    def parse_each_name(self,response):
        item = ExpertsExtractItem()
        content = response.xpath('//div[contains(@class, "post-content")]')
        expertise_block = content.xpath('ul/li/text()').extract()
        for i, ex in enumerate(expertise_block,1):    
            item['areas_of_expertise_%s' % i] = ex.strip()

        link = content.xpath('p/a/@href').extract_first()
        if not link:
            link = content.xpath('div/a/@href').extract_first()
        
        if link and '/news-releases/' not in link:
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            request.meta['item'] = item
            yield request



    def parse_each_expert(self, response):
        item = response.meta['item']
        item['faculty_page'] = response.url

        name = response.xpath('//h1[@class="main-title"]/text()').extract_first()
        if name:
            item['name'] = name.strip()

        title = response.xpath('//div[@class="profile-section profile-contact"]/*[contains(@class, "profile-dir-title")]/text()').extract_first()
        if title:
            item['title'] = title.strip()

        self.browser.get(item['faculty_page'])
        email = self.browser.find_element_by_xpath('//*[@class="profile-email"]/a')
        if email:
            email = email.get_attribute('href')
            if email:
                item['email'] = email.replace('mailto:', '').strip()

        website = response.xpath('//*[@class="profile-website"]/a/@href').extract_first()
        if website:
            item['website'] = website.strip()

        phone = response.xpath('//div[contains(@class, "profile-dir-phone")]/text()').extract_first()
        if phone:
            item['phone'] = phone.strip()

        bio_block = response.xpath('//h3[contains(string(), "Areas of Expertise")]/..')
        if bio_block:
            item['biography'] =  bio_block.xpath('string()').extract_first().replace('Areas of Expertise', '').strip().replace('\n', '. ')
        

        headshot = response.xpath('//div[@class="profile-section profile-contact"]/preceding-sibling::img/@src').extract_first()
        if headshot:
            item['headshot'] = headshot.strip()
        yield item
