from urllib.parse import urljoin

import scrapy

from ..helpers.retailer_id import create_retailer_id
from ..items import CreateDiscItem


class GolfdiscerSpider(scrapy.Spider):
    name = "golfdiscer"
    allowed_domains = ["golfdiscer.no"]
    start_urls = ["https://golfdiscer.no/collections/golfdiscer"]

    def parse(self, response):
        brands = response.css(".nav-merke > li")

        for brand in brands:
            brand_path = brand.css("a::attr(href)").get()
            brand_name = brand.css("a::text").get().strip()

            next_page = urljoin(response.url, brand_path)

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        for product in response.css(".product-inner"):
            disc = CreateDiscItem()
            disc["name"] = product.css(".product-loop-title > h3::text").get().strip()
            disc["image"] = product.css(".product-image img::attr(data-src)").get()
            disc["in_stock"] = product.css(".add-links-wrap span::text").get() != "Utsolgt"
            disc["spider_name"] = self.name
            disc["brand"] = brand
            disc["retailer"] = self.allowed_domains[0]
            disc["price"] = int(product.css(".money::text").get().split(",")[0])

            speed = product.css(".flight-numbers > li span::text").get()
            disc["speed"] = float(speed.strip()) if speed else None

            glide = product.css(".flight-numbers > li:nth-child(2)::text").get()
            disc["glide"] = float(glide.strip()) if glide else None

            turn = product.css(".flight-numbers > li:nth-child(3)::text").get()
            disc["turn"] = float(turn.strip()) if turn else None

            fade = product.css(".flight-numbers > li:nth-child(4)::text").get()
            disc["fade"] = float(fade.strip()) if fade else None

            url = product.css(".product-image > a::attr(href)").get()
            disc["url"] = urljoin("https://golfdiscer.no", url)
            disc["retailer_id"] = create_retailer_id(brand, url)

            yield disc

        next_page = response.css(".pagination-page a[title=Neste]::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
