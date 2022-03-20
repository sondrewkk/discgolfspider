from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy


class KrokholDgsSpider(scrapy.Spider):
    name = "krokholdgs"
    allowed_domains = ["krokholdgs.no"]
    start_urls = [
        "https://www.krokholdgs.no/categories/putter-disk",
        "https://www.krokholdgs.no/categories/midrange-disk",
        "https://www.krokholdgs.no/categories/fairwaydriver",
        "https://www.krokholdgs.no/categories/driver-disk",
    ]

    def parse(self, response):
        for product in response.css(".product-box-wrapper"):
            disc = CreateDiscItem()
            disc["name"] = product.css(".product_box_title_row a::text").get()
            disc["image"] = product.css(".image img::attr(src)").get()

            url = product.css(".product_box_title_row a::attr(href)").get()
            brand = product.css(".product::attr(data-manufacturer)").get()
            disc["url"] = url
            disc["spider_name"] = self.name
            disc["in_stock"] = int(product.css(".product::attr(data-quantity)").get()) > 0
            disc["retailer"] = self.allowed_domains[0]
            disc["retailer_id"] = create_retailer_id(brand, url)
            disc["brand"] = brand
            disc["price"] = int(product.css(".product-box::attr(data-price-including-tax)").get())
            disc["speed"] = None
            disc["glide"] = None
            disc["turn"] = None
            disc["fade"] = None

            yield disc

        next_page = response.css(".paginator_link_next::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
