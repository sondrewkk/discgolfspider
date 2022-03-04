from json.encoder import py_encode_basestring_ascii
from urllib.parse import urlparse
from urllib.parse import parse_qs
from ..items import CreateDiscItem

import scrapy


class SpinnvilldgSpider(scrapy.Spider):
    name = "spinnvilldg"
    allowed_domains = ["spinnvilldg.no"]
    start_urls = [
        "https://www.spinnvilldg.no/thought-space-athletics",
        "https://www.spinnvilldg.no/prodigy",
        "https://www.spinnvilldg.no/toby-dyes"
    ]

    def parse(self, response):
        load_button = response.css('button[data-hook="load-more-button"]').get()

        if load_button:
            next_page = response.url
            parsed_url = urlparse(response.url)
            query = parsed_url.query
            
            if not query:
                next_page += "?page=2"
            else:
                page = int(parse_qs(query)["page"][0]) + 1
                next_page = response.url.split("=")[0] + f"={page}"
            
            yield response.follow(next_page, callback=self.parse)
        else:
            for product in response.css("li[data-hook*=\"product-list-grid-item\"]"):
                disc = CreateDiscItem()
                disc["name"] = product.css("h3::text").get().replace("[", "").replace("]", "")
                disc["image"] = product.css('div[data-hook*="product-item-images"]::attr(style)').get().split('(', 1)[1].split(')', 1)[0]
                disc["url"] = product.css('a::attr(href)').get()
                disc["spider_name"] = self.name
                disc["in_stock"] = True
                disc["retailer"] = self.allowed_domains[0]
                disc["brand"] = response.url.split(".no/")[1].split("?")[0].replace("-", " ")
                disc["speed"] = None
                disc["glide"] = None
                disc["turn"] = None
                disc["fade"] = None

                price = product.css('span[data-hook="product-item-price-to-pay"]::text').get()
                disc["price"] = int(''.join(filter(str.isdigit, price.split(",")[0])))

                yield disc
