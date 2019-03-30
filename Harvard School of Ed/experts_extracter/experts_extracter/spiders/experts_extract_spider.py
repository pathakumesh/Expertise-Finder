# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem
from selenium import webdriver



class ExpertsExtractSpider(scrapy.Spider):
    chromedriver = "/Users/PathakUmesh/Downloads/chromedriver"
    browser = webdriver.Chrome(chromedriver)
    name = "expert_extract_spider"
    allowed_domains = ["gse.harvard.edu"]
    start_urls = ['https://www.gse.harvard.edu/faculty-directory/faculty-experts']

    def parse(self, response):
        experts = response.xpath('//div[@class="collapseSectionContent"]/a')
        for expert in experts:
            item = ExpertsExtractItem()    
            name = expert.xpath('text()').extract_first()
            link = expert.xpath('@href').extract_first()
            link = 'https://www.gse.harvard.edu' + link
            item['name'] = name
            item['faculty_page'] = link
            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            request.meta['item'] = item
            yield request
            
    def parse_each_expert(self, response):
        item = response.meta['item']
    
        title_block = response.xpath('//div[@class="page-layout__main-col-boundary"]/h3/text()').extract()
        for i,title in enumerate(title_block):
            item['title_%s' % (i+1)] = title.strip()
        
        #email is javascrip protected. Hence, selenium is used to extract the content
        # item['email'] = response.xpath('//span[@class="emailaddress"]/a/text()').extract_first()
        self.browser.get(item['faculty_page'])
        email = self.browser.find_element_by_xpath('//span[@class="emailaddress"]')
        item['email'] =  email.text
        
        
        details_block = response.xpath('//div[@class="detail"]/p')
        for detail in [i.strip() for i in details_block.xpath('text()').extract() if i.strip()]:
            matched = re.match(r'\d{3}', detail)
            if matched:
                item['phone'] = detail
        
        profile =  response.xpath('//div[@class="page-layout__main-col-boundary"]').extract_first()
        matched = re.search(r"<h2>Profile</h2>(.*?)(<p>|<!--)", profile, re.DOTALL)
        details = ''
        if matched:
            details = matched.group(1).strip()
            details = details.replace('<em>', '').replace('</em>', '')

        if not details:
            # profile = response.xpath('//h2[contains(text(), "Profile")]/following-sibling::p[1]')
            profile = response.xpath('//p[preceding-sibling::h2[1][contains(text(), "Profile")]]')
            for p in profile:
                details +=  ''.join(a for a in p.xpath('text()').extract())
        if details:
            item['profile'] = details
        
        personal_site_section = response.xpath('//span/strong[contains(text(), "Personal Site")]')
        if personal_site_section:
            personal_site = personal_site_section.xpath("../following-sibling::a[1]/@href").extract_first()
            item['personal_site'] = personal_site
        headshot = response.xpath('//div[@class="image"]/img/@src').extract_first()
        item['headshot'] = 'https://www.gse.harvard.edu' + headshot

        expertise_section = response.xpath('//div[@class="collapseSectionHeader" and contains(text(), "Areas of Expertise")]')
        if expertise_section:
            expertise = expertise_section.xpath('following-sibling::div[1][@class="collapseSectionContent"]/a/text()').extract()
            for i, value in enumerate(expertise):
                item['areas_of_expertise_%s' % (i+1)] = value
        yield item
