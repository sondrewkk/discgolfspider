# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DiscItem(scrapy.Item):
    name = scrapy.Field()
    image = scrapy.Field()
    spider_name = scrapy.Field()
    in_stock = scrapy.Field()
    url = scrapy.Field()
    retailer = scrapy.Field()
