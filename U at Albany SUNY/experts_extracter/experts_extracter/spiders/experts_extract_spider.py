# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem


class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["albany.edu"]
    start_urls = ['https://www.albany.edu/news/experts/alpha_experts.php']

    def parse(self, response):
        experts = response.xpath('//h1[contains(text(),"Faculty Experts")]/following-sibling::ul[1]//a')
        for expert in experts:
            item = ExpertsExtractItem()
            
            link = expert.xpath('@href').extract_first()
            link = 'https://www.albany.edu' + link if 'https:' not in link else link
            
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            yield request

            
    def parse_each_expert(self, response):
        item = ExpertsExtractItem()
        item['faculty_page'] = response.url

        intro_block = response.xpath('//p[contains(string(), "Department: ")]')
        name = response.xpath('//p[contains(string(), "Department: ")]/preceding-sibling::h1/text()').extract_first().strip()

        intro =  intro_block.xpath('string()').extract_first().strip()
        if 'Michele Caggana' in name:
            title, department =  re.split(r'[\n]+', intro)
            faculty = None
        elif 'Lei Zhu' in name:
            faculty, department =  re.split(r'[\n]+', intro)
            title = None
        else:
            title, faculty, department =  re.split(r'[\n]+', intro)
        department = department.replace('Department: ', '')
        item['name'] = name
        item['title'] = title
        item['faculty'] = faculty
        item['department'] = department

        expertise_block = response.xpath('//p[contains(string(), "Expertise:")]')
        expertise =  expertise_block.xpath('string()').extract_first().replace('\n', '').replace('Expertise:', '').strip()
        if '; ' in expertise:
            for i, ex in enumerate(re.split(r';', expertise),1):    
                item['areas_of_expertise_%s' % i] = ex.strip()
        else:
            for i, ex in enumerate(re.split(r',', expertise),1):
                item['areas_of_expertise_%s' % i] = ex.strip()

        contact_block = response.xpath('//p[contains(string(), "Campus phone") or contains(string(), "Campus email")]')
        contact =  contact_block.xpath('string()').extract_first().strip()
        phone =  re.findall(r'Campus phone:\s*(.*)[0-9]', contact)
        email = re.findall(r'Campus email:\s*(.*)', contact)
        if phone:
            item['phone'] = phone[0]
        if email:
            item['email'] = email[0]

        bio_block = response.xpath('//p[contains(string(), "Biography:")]/following-sibling::p')
        biography_full =  ' '.join(i.strip() for i in bio_block.xpath('string()').extract())
        item['biography_full'] = biography_full

        

        info_area = response.xpath('//div[@id="faculty-info-area"]')
        headshot = info_area.xpath('img/@src').extract_first()
        if headshot:
            item['headshot'] = 'https://www.albany.edu' + headshot if 'https://www.albany.edu' not in headshot else headshot

        biography_intro = info_area.xpath('div/p[@id="faculty-banner-text"]/text()').extract_first()
        if biography_intro:
            item['biography_intro'] = biography_intro.strip()
        yield item
