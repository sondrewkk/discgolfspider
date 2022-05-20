from attr import attributes
from scrapy.http import Headers
from scrapy import Request
from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem

import scrapy


class GuruSpider(scrapy.Spider):
    name = "guru"
    allowed_domains = ["gurudiscgolf.no"]
    start_urls = ["https://gurudiscgolf.no/wp-json/wc/v3/products?per_page=100&page=31"]
    http_user = ""
    http_pass = ""
    http_auth_domain = "gurudiscgolf.no"

    def parse(self, response):
        self.logger.debug("##### RUNNING PARSE ######")
        products = response.json()
        disc_products = [product for product in products if self.is_disc(product)]

        for disc_product in disc_products:
            disc = CreateDiscItem()
            disc["name"] = disc_product["name"]
            disc["image"] = disc_product["images"][0]["src"]
            disc["in_stock"] = True if disc_product["stock_status"] == "instock" else False
            
            url = disc_product["permalink"]
            disc["url"] = url
            disc["spider_name"] = self.name
            
            attributes = disc_products["attributes"]
            brand = self.get_attribute(attributes, "Produsent")
            disc["brand"] = brand
            disc["retailer"] = self.allowed_domains[0]
            disc["retialer_id"] = create_retailer_id(brand, url)
            disc["speed"] = self.get_attribute(attributes, "Speed")
            disc["glide"] = self.get_attribute(attributes, "Glide")
            disc["turn"] = self.get_attribute(attributes, "Turn")
            disc["fade"] = self.get_attribute(attributes, "Fade")

            price = disc_product["price"]
            if disc_product["tax_status"] == "taxable":
                price *= 1.25 # Add MVA

            disc["price"] = price

        # Check for next page
        headers: Headers = response.headers
        next_page = self.get_next_page(headers)

        if next_page is not None:
            yield Request(next_page, callback=self.parse)
        else:
            self.logger.debug(" ######### No next page ###########")


    def is_disc(self, product: dict) -> bool:
        product_type: str = product["categories"][0]["slug"]
        return product_type == "golfdiscer"


    def get_next_page(self, headers: Headers) -> str:
        link_header: str = headers.get("Link").decode("utf-8")
        next_page: str = None

        self.logger.debug(f"{link_header=}")

        if not link_header:
            return None

        links = link_header.split(",")

        for link in links:
            rel = link.split(";")[1]

            self.logger.debug(f"{rel=}")

            # If link header is of type next
            if rel.find("next") != -1:
                next_page = link.split(";")[0].replace("<", "").replace(">", "").strip()
                self.logger.debug(f"{next_page=}")
        
        return next_page

    
    def get_attribute(self, attributes: list, value: str) -> str:
        return next((attr["options"][0] for attr in attributes if attr["name"] == value), None)
