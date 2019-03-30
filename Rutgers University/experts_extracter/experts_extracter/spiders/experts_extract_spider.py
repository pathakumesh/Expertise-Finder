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
    allowed_domains = ["rutgers.edu"]
    
    def start_requests(self):
        formdata = {
            "a": "search",
            "f": "experts",
            "s": "topic",
            "p": "true",
            "q": "%",
            "submit": "Search"
        }
        request = scrapy.FormRequest(
                            'http://ucmweb.rutgers.edu/experts/index.php',
                            method="POST", 
                            formdata=formdata,
        )
        yield request
    
    def parse(self, response):
        print "page url: ", response.url
        experts = response.xpath('//form[@action="index.php"]/following-sibling::table/tr')
        for expert in experts:
            name = expert.xpath('td/strong/a/text()').extract_first()
            if name:
                link = expert.xpath('td/strong/a/@href').extract_first()
                link = "http://ucmweb.rutgers.edu/experts/" + link
                
                # Make a request to actual link for the blog to extract other info
                request =  scrapy.Request(link, callback=self.parse_each_expert)
                yield request
        

            
    def parse_each_expert(self, response):
        item = ExpertsExtractItem()
        item['faculty_page'] = response.url
        
        name = response.xpath('//span[contains(@class, "sbex_person_name")]/text()').extract_first()
        if name:
            item['name'] = name.strip()
        brief_info = [value.strip() for value in response.xpath('//span[contains(@class, "sbex_person_name")]/../text()').extract() if value.strip()]

        item['title'] = brief_info[0]
        item['department'] = brief_info[1] if len(brief_info) > 1 else None
        item['school_college'] = brief_info[2] if len(brief_info) > 2 else None
        item['campus'] = brief_info[3] if len(brief_info) > 3 else None
        item['other'] = brief_info[4] if len(brief_info) > 4 else None

        headshot = response.xpath('//span[contains(@class, "sbex_person_name")]/../preceding-sibling::td[1]/img/@src').extract_first()
        if headshot:
            item['headshot'] = headshot

        key_topics = response.xpath('//strong[contains(text(), "Key Topics")]/following-sibling::text()').extract()
        key_topics = ''.join(i for i in key_topics)
        if any(separator in key_topics for separator in [',', ';', '\n']):
            for j,value in enumerate(re.findall(r'([^,;\n]+)[,;\n]?', key_topics)):
                if not value.strip():
                    break
                item['key_topics_%s' % (j+1)] = value.strip()
        else:  
            item['key_topics_1'] = key_topics.strip()
        
        bio_section = response.xpath('//strong[contains(text(), "Expert\'s Biography")]/following-sibling::text()').extract()
        biography = ''. join(bio.replace('\n', '').strip() for bio in bio_section)
        if biography:
            item['biography'] = biography

        phone_section = response.xpath('//strong[contains(text(), "Office phone") or contains(text(), "Phone")]/following-sibling::text()').extract()
        phone =  [phone.replace('\n', '').strip() for phone in phone_section if phone.strip()]
        if phone:
            phone = phone[0].replace(':', '')
            item['phone'] = phone
            if 'ext.' in phone.lower():
                phone,extension = [i.strip() for i in phone.split('Ext.')]
                item['phone'] = phone
                item['extension'] = extension

        
        self.browser.get(item['faculty_page'])
        email = self.browser.find_element_by_xpath('//strong[contains(text(), "Email")]/following-sibling::a[1]')
        if email:
            item['email'] = email.text

        # email = response.xpath('//strong[contains(text(), "Email")]/following-sibling::a[1]/text()').extract_first()
        # if email:
            # item['email'] = email

        personal_site = response.xpath('//strong[contains(text(), "Web Page")]/following-sibling::a[1]/text()').extract_first()
        if personal_site:
            item['personal_site'] = personal_site

        yield item