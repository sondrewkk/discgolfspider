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
    retailer_id = scrapy.Field()
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

    def has_flight_specs(self) -> bool:
        return all(self.get(field) is not None for field in ["speed", "glide", "turn", "fade"])


class CreateDiscItem(scrapy.Item):
    name = scrapy.Field()
    image = scrapy.Field()
    spider_name = scrapy.Field()
    in_stock = scrapy.Field()
    url = scrapy.Field()
    retailer = scrapy.Field()
    retailer_id = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    speed = scrapy.Field()
    glide = scrapy.Field()
    turn = scrapy.Field()
    fade = scrapy.Field()

    def dict(self):
        return self.__dict__["_values"]

    def __repr__(self):
        return f"{self.get('name')} ({self.get('url')})"

    def __str__(self):
        return f"{self.get('name')} ({self.get('url')})"

    def has_flight_specs(self) -> bool:
        return all(self.get(field) is not None for field in ["speed", "glide", "turn", "fade"])
