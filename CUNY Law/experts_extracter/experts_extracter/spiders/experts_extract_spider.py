# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem


class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["law.cuny.edu"]
    start_urls = ['http://www.law.cuny.edu/faculty/experts.html']

    def parse(self, response):
        experts = response.xpath('//table[@class="directory-layout"]//tr')
        for expert in experts[2:]:
            item = ExpertsExtractItem()
            info_block, areas_of_expertise = expert.xpath('td')

            name = info_block.xpath('p/a[contains(@href, "directory")]/text()').extract_first()
            if name:
                item['name'] = name.strip()
            
            link = info_block.xpath('p/a[contains(@href, "directory")]/@href').extract_first()
            link = "http://www.law.cuny.edu/faculty/" + link if 'http://www.law.cuny.edu/faculty/' not in link else link

            email = info_block.xpath('p/a[contains(@href, "mailto:")]/text()').extract_first()
            if email:
                item['email'] = email.strip()
            phone = info_block.xpath('p[contains(text(), "Office")]/text()').extract_first()
            if phone:
                item['phone'] = phone.split('Office:')[-1].strip()
            
            expertise = areas_of_expertise.xpath('ul/li/text()').extract()
            for i, expertise in enumerate(expertise, 1):
                item['areas_of_expertise_%s' % i] = expertise.strip()

            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            request.meta['item'] = item
            yield request

            
    def parse_each_expert(self, response):
        
        item = response.meta['item']

        bio_block =  response.xpath('//div[@class="l-col"]/p')
        biography = bio_block[0].xpath('string()').extract_first().replace('\t', '').replace('\n', '')
        more_para =  bio_block[0].xpath("following-sibling::p[not (preceding-sibling::div)]")
        if more_para:
            for para in more_para:
                biography += ' ' +  para.xpath('string()').extract_first().replace('\t', '').replace('\n', '')
        item['biography'] = biography

        item['faculty_page'] = response.url

        headshot = response.xpath('//div[@class="r-col"]//img/@src').extract_first()
        if headshot:
            item['headshot'] = response.url.rsplit('/',1)[0] + '/' + headshot

        yield item
