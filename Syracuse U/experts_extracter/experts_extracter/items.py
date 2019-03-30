# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ExpertsExtractItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    title = scrapy.Field()

    phone = scrapy.Field()
    email = scrapy.Field()
    personal_site = scrapy.Field()
    twitter = scrapy.Field()
    biography = scrapy.Field()
    faculty_page = scrapy.Field()
    page_link = scrapy.Field()
    headshot = scrapy.Field()
    
    
    areas_of_expertise_1 = scrapy.Field()
    areas_of_expertise_2 = scrapy.Field()
    areas_of_expertise_3 = scrapy.Field()
    areas_of_expertise_4 = scrapy.Field()
    areas_of_expertise_5 = scrapy.Field()
    areas_of_expertise_6 = scrapy.Field()
    areas_of_expertise_7 = scrapy.Field()
    areas_of_expertise_8 = scrapy.Field()
    areas_of_expertise_9 = scrapy.Field()
    areas_of_expertise_10 = scrapy.Field()
    areas_of_expertise_11 = scrapy.Field()
    areas_of_expertise_12 = scrapy.Field()
    areas_of_expertise_13 = scrapy.Field()
    pass
