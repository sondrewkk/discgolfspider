from ..items import DiscItem

import scrapy
import re

class AceshopSpider(scrapy.Spider):
    name = "aceshop"
    allowed_domains = ["aceshop.no"]
    start_urls = [
        "https://aceshop.no/categories/discer"
    ]

    def parse(self, response):
        for product in response.css(".product-box-wrapper"):
            disc = DiscItem()
            disc["name"] = product.css(".product_box_title_row a::text").get()
            disc["image"] = product.css(".image img::attr(src)").get()
            disc["url"] = product.css(".product_box_title_row a::attr(href)").get()
            disc["spider_name"] = self.name
            disc["in_stock"] = int(product.css(".product::attr(data-quantity)").get()) > 0
            disc["retailer"] = self.allowed_domains[0]
            disc["brand"] = product.css("p.manufacturers::text").get().strip().title()
            disc["price"] = int(product.css(".product-box::attr(data-price-including-tax)").get())
            
            flight_specs = product.css(".product_box_tag span::text").getall()
            
            if len(flight_specs) == 4:
                flight_specs = [float(numeric_string.replace(",", ".")) for numeric_string in flight_specs]
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs
            else:
                self.logger.warning(f"Did not find flight spec for disc with name { disc['name'] }")
                disc["speed"] = None
                disc["glide"] = None
                disc["turn"] = None
                disc["fade"] = None
            
            yield disc

        next_page = response.css(".paginator_link_next::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    