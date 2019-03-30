# -*- coding: utf-8 -*-

import re
import scrapy
import logging as log
from experts_extracter.items import ExpertsExtractItem



x = ['Aaron Lecklider', 'Adenrele Awotona', 'Atreya Chakraborty', 'Banu Ozkazanc-Pan', 'Carol Hall Ellenbecker', 
'Christian Weller', 'Cinzia Solari', 'Darren Kew', 'Deborah Mahony', 'Donna Haig Friedman', 'Elizabeth Dugan', 
'Ellen Douglas', "Erin O'Brien", 'Georgianna Melendez', 'Jane Cloutterbuck', 'Jean Rhodes', 'Jurui Zhang', 
'Kristin Murphy', 'Laura Hayman', 'Leila Farsakh', 'Lisa Cosgrove', 'Lucia Silva Gao', 'Maria Ivanova', 
'Marion Winfrey', 'Maurice "Mo" Cunningham', 'Nardia Haigh', "Padraig O'Malley", 'Paul Watanabe', 'Philip DiSalvio', 
'Rachel Rubin', 'Randy Albelda', 'Robert L. Turner', 'Sharon Lamb', 'Sherry Penney', 'Stephan Manning', 'Suzanne Leveille', 
'Vesela Veleva', 'Werner Kunz']
print len(x)


class ExpertsExtractSpider(scrapy.Spider):
    name = "expert_extract_spider"
    allowed_domains = ["umb.edu"]
    start_urls = ['https://www.umb.edu/news_events_media/communications/for_the_media/experts#panel-l-2']

    def parse(self, response):
        experts = response.xpath('//div[@class="unit-33"]/div[@data-tools="accordion"]/div[contains(@class,"accordion-panel")]')
        for expert in experts:
            areas_of_expertise = expert.xpath('text()').extract_first().strip()
            link = expert.xpath('a/@href').extract_first()
            link = "https://www.umb.edu" + link if 'www.umb.ed' not in link else link
            
            name = expert.xpath('a/text()').extract_first()
            new_link = title_for_special_case(name)
            link = new_link if new_link else link
            link = link.replace('http:', 'https:')
            # Make a request to actual link for the blog to extract other info
            request =  scrapy.Request(link, callback=self.parse_each_expert)
            request.meta['areas_of_expertise'] = areas_of_expertise

            request.meta['name'] = name
            # request.meta['dont_redirect'] = True
            # request.meta['handle_httpstatus_all'] = True
            yield request

            
    def parse_each_expert(self, response):
        item = ExpertsExtractItem()
        areas_of_expertise = response.meta['areas_of_expertise']
        initial_expertise = [a.lower().strip() for a in re.split(r',|;', areas_of_expertise)]
        department = response.xpath('//div[@class="unit-100 masthead-inner"]')
        try:
            department = department.xpath('string()').extract()[0].strip()

        except:
            print 'EXCEPTION: ', response.meta['name']
            return
        name = response.xpath('//h3[@id="bioName"]/strong/text()').extract_first()
        title_block = response.xpath('//h3[@id="bioName"]/following-sibling::p[1]')
        for i,title in enumerate(title_block.xpath('span/text()').extract()):
            item['title_%s' % (i+1)] = title.strip()
        item['name'] = name
        item['department'] = department
        item['phone'] = response.xpath('//li[@class="tel"]/a/text()').extract_first()
        item['email'] = response.xpath('//li[@class="email"]/a/text()').extract_first()
        item['website'] = response.xpath('//li[@class="website"]/a/text()').extract_first()
        item['faculty_page'] = response.url
        headshot = response.xpath('//img[@class="profile_photo"]/@src').extract_first()
        if headshot:
            item['headshot'] = headshot


        areas_of_expertise = response.xpath('//h4[text()="Areas of Expertise"]/following-sibling::p[1]/text()').extract_first()
        detailed_expertise = []
        if areas_of_expertise:
            detailed_expertise = [a.lower().strip() for a in re.split(r',|;', areas_of_expertise)]
        merged_expertise = get_merged_expertise(initial_expertise, detailed_expertise)
        for i, expertise in enumerate(merged_expertise):
            if i>20:
                break
            item['areas_of_expertise_%s' % (i+1)] = expertise
        
        additional_info = ''
        info = response.xpath('//*[preceding-sibling::h4[contains(text(), "Additional Information")]]')
        for i in info:
            if i.xpath('string()').extract_first():
                sub_info = i.xpath('string()').extract_first().strip()
                if sub_info:
                    additional_info += sub_info + '\n'
        if additional_info:
            item['additional_info'] = additional_info
        yield item

def title_for_special_case(name):
    if re.match(r'robert.*turner', name,re.IGNORECASE):
        return "https://www.umb.edu/commonwealth_compact/about/staff/robert_turner"
    if re.match(r'georgianna\s*melendez', name,re.IGNORECASE):
        return "https://www.umb.edu/commonwealth_compact/about/staff/georgianna_melendez"

def get_merged_expertise(initial_list, detailed_list):
    merged_list = list(set(initial_list) | set(detailed_list))
    merged_list.sort(reverse=True)
    final_list = []
    for i in merged_list:
        if not any(i in x for x in final_list):
            final_list.append(i)
    return final_list
