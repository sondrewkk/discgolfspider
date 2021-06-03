from ..items import DiscItem

import scrapy

class KrokholDgsSpider(scrapy.Spider):
    name = "krokholdgs"
    allowed_domains = ["krokholdgs.no"]
    start_urls = [
        "https://www.krokholdgs.no/categories/putter-disk",
        "https://www.krokholdgs.no/categories/midrange-disk",
        "https://www.krokholdgs.no/categories/fairwaydriver",
        "https://www.krokholdgs.no/categories/driver-disk"
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
            disc["brand"] = product.css(".product::attr(data-manufacturer)").get()
            disc["price"] = product.css(".product-box::attr(data-price-including-tax)").get()
            
            flight_specs = product.css(".product_box_tag span::text").getall()
            
            if len(flight_specs) == 4:
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs
            
            yield disc

        next_page = response.css(".paginator_link_next::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    