# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DiscItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    image = scrapy.Field()
    spider_name = scrapy.Field()
    in_stock = scrapy.Field()
    url = scrapy.Field()
    retailer = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    speed = scrapy.Field()
    glide = scrapy.Field()
    turn = scrapy.Field()
    fade = scrapy.Field()
    created = scrapy.Field()
    last_updated = scrapy.Field()

    def dict(self):
        return self.__dict__["_values"]

class CreateDiscItem(scrapy.Item):
    name = scrapy.Field()
    image = scrapy.Field()
    spider_name = scrapy.Field()
    in_stock = scrapy.Field()
    url = scrapy.Field()
    retailer = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    speed = scrapy.Field()
    glide = scrapy.Field()
    turn = scrapy.Field()
    fade = scrapy.Field()

    def dict(self):
        return self.__dict__["_values"]
