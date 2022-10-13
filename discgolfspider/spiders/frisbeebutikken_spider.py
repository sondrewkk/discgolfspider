from urllib.parse import parse_qs, urlparse
from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy

class FrisbeebutikkenSpider(scrapy.Spider):
    name = "frisbeebutikken"
    allowed_domains = ["frisbeebutikken.no"]
    start_urls = ["https://frisbeebutikken.no/categories/golfdisker/sort-by/1/?page=1"]


    def parse(self, response):
        for product in response.css(".product-box"):
            
            disc = CreateDiscItem()
            
            try: 
                disc["name"] = product.css(".title::text").get()
                disc["image"] = product.css(".image img::attr(src)").get()
                
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

                price = -9999
                sale_price: str = product.css(".has-special-price > span::text").get()
                regular_price: str = product.css(".price::text").get()

                if sale_price:
                    price = self.price_to_int(sale_price)
                else:
                    price = self.price_to_int(regular_price)

                disc["price"] = price

                yield disc
            except Exception as e:
                self.logger.error(f"Error parsing disc: {disc['name']}({disc['url']})")
                self.logger.error(e)

        next_page = response.css(".paginator_link_next::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    
    def price_to_int(self, price) -> int:
        price_number = price.strip().split(",")[0]
        return int(price_number)
