from json.encoder import py_encode_basestring_ascii
from urllib.parse import urlparse
from urllib.parse import parse_qs
from ..items import CreateDiscItem

import scrapy


class SpinnvilldgSpider(scrapy.Spider):
    name = "spinnvilldg"
    allowed_domains = ["spinnvilldg.no"]
    start_urls = [
        "https://www.spinnvilldg.no/shop?Merke=Thought+Space+Athletics&page=1",
        "https://www.spinnvilldg.no/shop?Merke=Prodigy&page=1",
    ]

    def parse(self, response):
        for product in response.css("li[data-hook*=\"product-list-grid-item\"]"):
            disc = CreateDiscItem()
            disc["name"] = product.css("h3::text").get().replace("[", "").replace("]", "")
            disc["image"] = product.css("div[data-hook*=\"product-item-images\"]::attr(style)").get().split("(", 1)[1].split(")", 1)[0]
            disc["url"] = product.css("a::attr(href)").get()
            disc["spider_name"] = self.name
            disc["retailer"] = self.allowed_domains[0]
            disc["brand"] = response.url.split("Merke=")[1].split("&")[0].replace("+", " ")
            disc["speed"] = None
            disc["glide"] = None
            disc["turn"] = None
            disc["fade"] = None

            out_of_stock = response.css("span[data-hook=\"product-item-out-of-stock\"]")

            if not out_of_stock:
                disc["in_stock"] = True
                
                price = product.css("span[data-hook=\"product-item-price-to-pay\"]::text").get()
                disc["price"] = int(''.join(filter(str.isdigit, price.split(",")[0])))

                yield disc
            
        next_page_active = response.css("a[data-hook=next]::attr(aria-disabled)").get() == "false"
        
        if next_page_active:
            url_splitted = response.url.rsplit("=", 1)
            print(url_splitted)
            page = int(url_splitted[1]) + 1
            next_page = f"{url_splitted[0]}={page}"

            yield response.follow(next_page, callback=self.parse)
 