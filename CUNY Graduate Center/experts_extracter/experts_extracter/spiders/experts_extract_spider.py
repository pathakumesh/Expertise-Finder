# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem


class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["gc.cuny.edu"]
    start_urls = ['https://www.gc.cuny.edu/About-the-GC/Administrative-Services/Office-of-Communications-and-Marketing/Resources/Media-Experts']

    def parse(self, response):
        experts = response.xpath('//div[@class="m_expert"]')
        for expert in experts:
            item = ExpertsExtractItem()

            name = expert.xpath('h2/a/text()').extract_first()
            if name:
                item['name'] = name.strip()
            
            link = expert.xpath('h2/a/@href').extract_first()

            link = "https://www.gc.cuny.edu" + link if 'https:' not in link else link

            title_block = expert.xpath('h2/following-sibling::p[1]/i/text()').extract()
            for i, title in enumerate(title_block , 1):
                item['title_%s' % i] = title.strip()
            
            email = expert.xpath('h2/following-sibling::p[1]/a/text()').extract_first()
            if email:
                item['email'] = email.strip()
            
            expertise_block = expert.xpath('h2/following-sibling::p[2]')
            if expertise_block:
                expertise = expertise_block.xpath('string()').extract_first()
                expertise = expertise.replace('SPECIALIZATIONS:', '').replace('\r', '').replace('\n', '').strip()
                for i, ex in enumerate(re.split(';|,',expertise), 1):
                    item['areas_of_expertise_%s' % i] = ex.strip()
            # yield item

            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            request.meta['item'] = item
            request.meta['expertise_index'] = i+1
            yield request

            
    def parse_each_expert(self, response):
        expertise_index = response.meta['expertise_index']
        item = response.meta['item']
        item['faculty_page'] = response.url

        department_block = response.xpath('//strong[contains(text(), "Program")]/following-sibling::a')
        if department_block:
            for i, department in enumerate(department_block , 1):
                item['department_%s' % i] = department.xpath('text()').extract_first().strip()

        phone = response.xpath('//strong[contains(text(), "Phone")]/../text()').extract_first()
        if phone:
            item['phone'] = phone.strip()
        
        website = response.xpath('//a[contains(text(), "Website")]/@href').extract_first()
        if website:
            item['website'] = website.strip()

        areas_of_expertise =  response.xpath('//strong[contains(text(), "Research Interest")]/../text()').extract_first()
        if areas_of_expertise:
            for i, ex in enumerate(re.split(';|,',areas_of_expertise), expertise_index):
                    item['areas_of_expertise_%s' % i] = ex.strip()

        bio_block =  response.xpath('//div[@class="detailbox2"]/div[@class="facultydata"]')
        if bio_block:
            item['biography'] = ''.join(b.replace('\r','').replace('\n',' ').replace('\t', '') for b in bio_block.xpath('string()').extract())

        headshot = response.xpath('//div[@id="facultyimage"]/img/@src').extract_first()
        if headshot:
            item['headshot'] = "https://www.gc.cuny.edu" + headshot if 'https://www.gc.cuny.edu' not in headshot else headshot

        yield item
