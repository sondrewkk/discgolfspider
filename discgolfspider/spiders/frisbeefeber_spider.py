from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy


class FrisbeefeberSpider(scrapy.Spider):
    name = "frisbeefeber"
    allowed_domains = ["frisbeefeber.no"]
    start_urls = ["https://www.frisbeefeber.no/brands"]

    def parse(self, response):
        brands = response.css(".box .row")

        for brand in brands:
            brand_name = brand.css("a::text").get()
            next_page = brand.css("a::attr(href)").get()

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        products = response.css(".product-box")

        for product in products:
            disc = CreateDiscItem()
            disc["name"] = product.css(".title::text").get()
            disc["image"] = product.css(".image-mainimage > img::attr(src)").get()

            url = product.css(".title::attr(href)").get()
            disc["url"] = url
            disc["spider_name"] = self.name
            disc["in_stock"] = int(product.css(".product::attr(data-quantity)").get()) > 0
            disc["retailer"] = self.allowed_domains[0]
            disc["retailer_id"] = create_retailer_id(brand, url)
            disc["brand"] = brand

            price = product.css(".price::text").get()
            if price:
                disc["price"] = int(price.strip().replace(".", "").split(",")[0])

            disc["speed"] = None
            disc["glide"] = None
            disc["turn"] = None
            disc["fade"] = None

            yield disc

        next_page = response.css(".paginator_link_next::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
