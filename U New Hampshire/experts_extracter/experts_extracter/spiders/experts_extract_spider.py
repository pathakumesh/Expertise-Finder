# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem


"""
more department/colleges:
https://www.unh.edu/unhtoday/expert/edwards-katie
https://www.unh.edu/unhtoday/expert/cashman-holly
https://www.unh.edu/unhtoday/expert/brettschneider-marla
https://www.unh.edu/unhtoday/expert/jones-lisa
https://www.unh.edu/unhtoday/expert/hojjat-ali
https://www.unh.edu/unhtoday/expert/mcmahon-gregory
https://www.unh.edu/unhtoday/expert/lee-jade
https://www.unh.edu/unhtoday/expert/hiley-sharp-erin
https://www.unh.edu/unhtoday/expert/glauber-rebecca
https://www.unh.edu/unhtoday/expert/baumgartner-kabria
"""
class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["unh.edu"]
    start_urls = ['https://www.unh.edu/unhtoday/news/experts']

    def parse(self, response):
        print "page url: ", response.url
        experts = response.xpath('//section[@id="block-system-main"]//h2[@class="field-content"]/a')
        for expert in experts:
            link = expert.xpath('@href').extract_first()
            link = "https://www.unh.edu" + link

            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            yield request
        
        next_page = response.xpath('//li[@class="next"]/a')
        if next_page:
            next_page_url = "https://www.unh.edu" + next_page.xpath('@href').extract_first()
            yield scrapy.Request(next_page_url)

            
    def parse_each_expert(self, response):
        item = ExpertsExtractItem()
        item['faculty_page'] = response.url
        
        name = response.xpath('//h1[@class="page-title"]/text()').extract_first()
        if name:
            item['name'] = name
        
        title_block = response.xpath('//div[contains(@class, "field-name-field-expert-professional-title")]')
        if title_block:
            item['title'] = title_block.xpath('string()').extract_first()
        
        bio_block = response.xpath('//div[contains(@class, "panel-pane pane-entity-field pane-node-body")]')
        if bio_block:
            item['biography'] = bio_block.xpath('string()').extract()[0].strip()
        
        expertise_block = response.xpath('//div[@class="field-label" and contains(text(), "Expertise")]/following-sibling::div[1][@class="field-items"]/div')
        expertise_list = list()
        for expertise in expertise_block:
          expertise_list.append(expertise.xpath('text()').extract_first())
        for i, expertise in enumerate(expertise_list):
            if i>20:
                break
            item['areas_of_expertise_%s' % (i+1)] = expertise

        department_block = response.xpath('//div[@class="field-label" and contains(text(), "Department/College")]/following-sibling::div[1][@class="field-items"]/div')
        if department_block:
            item['college'] = department_block[0].xpath('text()').extract_first()
        if department_block and len(department_block)>1:
            item['department'] = department_block[1].xpath('text()').extract_first()
        if len(department_block)>2:
            print 'MORE DEPARTMENT: ', response.url        
        
        headshot = response.xpath('//div[contains(@class, "field-name-field-contributor-photo field-type-image")]//img/@src').extract_first()
        if headshot:
            item['headshot'] = headshot
         
        email = response.xpath('//div[contains(@class, "field-name-field-contributor-email")]//a/text()').extract_first()
        if email:
            item['email'] = email

        phone_block = response.xpath('//div[contains(@class, "field-name-field-contributor-phone")]/div[@class="field-items"]/div')
        if phone_block:
            item['office_contact'] = phone_block.xpath('text()').extract_first()

        phone_block = response.xpath('//div[contains(@class, "field-name-field-expert-mobile-phone")]/div[@class="field-items"]/div')
        if phone_block:
            item['personal_contact'] = phone_block.xpath('text()').extract_first()

        
        personal_site_block = response.xpath('//div[contains(@class, "field-name-field-expert-homepage")]/div[@class="field-items"]/div/a')
        if personal_site_block:
            item['personal_site'] = personal_site_block.xpath('@href').extract_first()
        yield item

def title_for_special_case(name):
    if re.match(r'robert.*turner', name,re.IGNORECASE):
        return "https://www.umb.edu/commonwealth_compact/about/staff/robert_turner"
    if re.match(r'georgianna\s*melendez', name,re.IGNORECASE):
        return "https://www.umb.edu/commonwealth_compact/about/staff/georgianna_melendez"


