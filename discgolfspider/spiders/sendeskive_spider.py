import re
import time
from discgolfspider.items import CreateDiscItem
from discgolfspider.helpers.retailer_id import create_retailer_id

import scrapy


class SendeskiveSpider(scrapy.Spider):
    name = "sendeskive"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.api_base_url = "https://sendeplate-no.myshopify.com/admin/api/2023-01"
        self.shop_base_url = "https://sendeskive.no"
        self.token = settings["SENDESKIVE_API_KEY"]
        
        if not self.token:
            self.logger.error("No token found for sendeskive.no")
            return

        self.headers = {
            "X-Shopify-Access-Token": self.token
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def start_requests(self):
        url = f"{self.api_base_url}/products.json?status=active&product_type=Frisbee&limit=100"
        yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        products = response.json()['products']
        self.logger.debug(f"Found {len(products)} products")
        self.logger.debug(f"First Product: {products[0]}")

        if len(products) == 0:
            self.logger.error("No products found for discsjappa.no")
            return
      
        # Remove unwanted products  
        products = self.clean_products(products)

        for product in products:
            brand = product['vendor']
            if brand != "Discsjappa":
                url = f"{self.api_base_url}/products/{product['id']}/metafields.json"        
                yield scrapy.Request(url, headers=self.headers, callback=self.parse_product_with_metafields, cb_kwargs=dict(product=product))

        # Check if response containt next link header and foilow it if it does
        if "link" in response.headers:
            links = response.headers["link"].decode("utf-8")
            next_link_match = re.search('<([^>]+)>; rel="next"', links)

            if next_link_match:
                next_link = next_link_match.group(1)
                yield scrapy.Request(next_link, headers=self.headers, callback=self.parse)
  
    def parse_product_with_metafields(self, response, product):
        self.logger.debug(f"Product: {product['title']}")
        time.sleep(0.5) # Shopify API rate limit is 2 requests per second

        metafields = response.json()["metafields"]

        try:
            disc = CreateDiscItem()
            disc["name"] = product["title"]
            disc["spider_name"] = self.name
            disc["brand"] = self.get_brand(metafields)
            disc["retailer"] = "sendeskive.no"
            disc["url"] = self.create_product_url(product["handle"])
            disc["retailer_id"] = create_retailer_id(disc["brand"], disc["url"])
            disc["image"] = product["image"]["src"]

            variants = product["variants"]
            disc["in_stock"] = True if self.get_inventory_quantity(variants) > 0 else False
            disc["price"] = self.get_price_from_variant(variants[0])
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = self.get_flight_spec(metafields)

            yield disc
        except Exception as e:
            self.logger.error(f"Error parsing disc: {product['title']}({self.create_product_url(product['handle'])}), reason: {e}")

    def clean_products(self, products):
        self.logger.debug(f"Cleaning {len(products)} products")

        # Remove products with no variants
        products = [product for product in products if len(product["variants"]) > 0]

        # Remove products that has wrong product type
        products = [product for product in products if product["product_type"].lower() == "frisbee"]

        # Remove products that has -sett in the name
        products = [product for product in products if "-sett" not in product["title"].lower()]

        self.logger.debug(f"Cleaned products: {len(products)}")

        return products

    def create_product_url(self, product_handle: str):
        return f"{self.shop_base_url}/products/{product_handle}"

    def get_inventory_quantity(self, variants) -> float:
        return sum([float(variant["inventory_quantity"]) for variant in variants])

    def get_price_from_variant(self, variant) -> float:
        return float(variant["price"])

    def get_flight_spec(self, metafields) -> tuple:
        speed = glide = turn = fade = None

        for metafield in metafields:
            if metafield["key"] == "speed":
                speed = float(metafield["value"])
            elif metafield["key"] == "glide":
                glide = float(metafield["value"])
            elif metafield["key"] == "turn":
                turn = float(metafield["value"])
            elif metafield["key"] == "fade":
                fade = float(metafield["value"])

        # Raise exception if any of the flight spec values are missing
        has_none_values = all(value is None for value in (speed, glide, turn, fade))
        self.logger.debug(f"Has none values: {has_none_values}")

        if has_none_values:
            raise Exception(f"Missing flight spec values: (speed, glide, turn, fade) = {speed, glide, turn, fade}")

        return speed, glide, turn, fade

    def get_brand(self, metafields) -> str:
        brand_metafield = [metafield for metafield in metafields if metafield["namespace"] == "merke"]
        if len(brand_metafield) == 0:
            raise Exception("No brand metafield found")

        return brand_metafield[0]["value"]