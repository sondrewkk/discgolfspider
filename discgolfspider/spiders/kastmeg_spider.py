import re
import time
from discgolfspider.items import CreateDiscItem
from discgolfspider.helpers.retailer_id import create_retailer_id

import scrapy


class KastmegSpider(scrapy.Spider):
    name = "kastmeg"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.baseUrl = "https://kastmeg.myshopify.com/admin/api/2023-01"
        self.token = settings["KASTMEG_API_KEY"]
        self.retailer = "kastmeg.no"

        if not self.token:
            self.logger.error(f"No token found for {self.retailer}")
            return

        self.headers = {
            "X-Shopify-Access-Token": self.token
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def start_requests(self):
        url = f"{self.baseUrl}/products.json?status=active&limit=100"
        yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        products = response.json()['products']

        if len(products) == 0:
            self.logger.error(f"No products found for {self.retailer}")
            return

        # Remove unwanted products
        products = self.clean_products(products)

        for product in products:
            try:
                time.sleep(0.5)  # Sleep to avoid rate limit
                disc = CreateDiscItem()
                disc["name"] = product["title"]
                disc["spider_name"] = self.name
                disc["brand"] = product["vendor"]
                disc["retailer"] = self.retailer
                disc["url"] = self.create_product_url(product["handle"])
                disc["retailer_id"] = create_retailer_id(disc["brand"], disc["url"])
                disc["image"] = product["image"]["src"]

                variants = product["variants"]
                disc["in_stock"] = self.get_inventory_quantity(variants) > 0
                disc["price"] = self.get_price_from_variant(variants[0])
                yield disc
            except Exception as e:
                self.logger.error(f"Error parsing disc: {product['title']}({self.create_product_url(product['handle'])})")
                self.logger.error(e)

        # Check if response containt next link header and follow it if it does
        if "link" in response.headers:
            links = response.headers["link"].decode("utf-8")
            next_link_match = re.search('<([^>]+)>; rel="next"', links)

            if next_link_match:
                next_link = next_link_match.group(1)
                yield scrapy.Request(next_link, headers=self.headers, callback=self.parse)

    def clean_products(self, products):
        self.logger.debug(f"Cleaning {len(products)} products")

        # Remove products with no variants
        products = [product for product in products if len(product["variants"]) > 0]

        # Remove if prodiuct is a package
        products = [product for product in products if "pakke" not in product["tags"]]

        self.logger.debug(f"Cleaned products: {len(products)}")

        return products

    def create_product_url(self, product_handle: str):
        return f"https://{self.retailer}/products/{product_handle}"

    def get_inventory_quantity(self, variants) -> float:
        return sum([float(variant["inventory_quantity"]) for variant in variants])

    def get_price_from_variant(self, variant) -> float:
        return float(variant["price"])
