from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy

class FrisbeebutikkenSpider(scrapy.Spider):
    name = "frisbeebutikken"
    allowed_domains = ["shop.frisbeebutikken.no"]
    start_urls = ["https://shop.frisbeebutikken.no/categories/golfdisker"]


    def parse(self, response):
        for product in response.css(".product-box"):
            disc = CreateDiscItem()
            disc["name"] = product.css(".title::text").get()
            disc["image"] = product.css(".image-mainimage img::attr(src)").get()
            
            brand = product.css(".manufacturer-box img::attr(alt)").get()
            url = product.css(".product_box_title_row a::attr(href)").get()
            disc["url"] = url
            disc["spider_name"] = self.name
            disc["brand"] = brand
            disc["retailer"] = "frisbeebutikken.no"
            disc["retailer_id"] = create_retailer_id(brand, url)
            disc["in_stock"] = int(product.css(".product::attr(data-quantity)").get()) > 0
            disc["speed"] = None
            disc["glide"] = None
            disc["turn"] = None
            disc["fade"] = None

            disc["price"] = None
            price = product.css(".price::text").get()

            if price:
                disc["price"] = int(price.strip().split(",")[0])

            yield disc

        next_page = response.css(".paginator_link_next::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
