import re
import time
from discgolfspider.items import CreateDiscItem
from discgolfspider.helpers.retailer_id import create_retailer_id

import scrapy


class DiscsjappaSpider(scrapy.Spider):
    name = "discsjappa"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.token = settings["DISCSJAPPA_API_KEY"]
        
        if not self.token:
            self.logger.error("No token found for discsjappa.no")
            return

        self.headers = {
            "X-Shopify-Access-Token": self.token
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def start_requests(self):
        url = "https://discsjappa1.myshopify.com/admin/api/2023-01/products.json?status=active&limit=100"
        yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        products = response.json()['products']

        if len(products) == 0:
            self.logger.error("No products found for discsjappa.no")
            return
      
        # Remove unwanted products  
        products = self.clean_products(products)

        for product in products:
            url = f"https://discsjappa1.myshopify.com/admin/api/2023-01/products/{product['id']}/metafields.json"        
            yield scrapy.Request(url, headers=self.headers, callback=self.parse_product_with_metafields, cb_kwargs=dict(product=product))

        # Check if response containt next link header and follow it if it does
        if "link" in response.headers:
            links = response.headers["link"].decode("utf-8")
            next_link_match = re.search('<([^>]+)>; rel="next"', links)

            if next_link_match:
                next_link = next_link_match.group(1)
                yield scrapy.Request(next_link, headers=self.headers, callback=self.parse)
  
    def parse_product_with_metafields(self, response, product):
        self.logger.debug(f"Product: {product['title']}")
        
        try:
            time.sleep(0.5) # Sleep to avoid rate limit

            disc = CreateDiscItem()
            disc["name"] = product["title"]
            disc["spider_name"] = self.name
            disc["brand"] = product["vendor"]
            disc["retailer"] = "discsjappa.no"
            disc["url"] = self.create_product_url(product["handle"])
            disc["retailer_id"] = create_retailer_id(disc["brand"], disc["url"])
            disc["image"] = product["image"]["src"]

            variants = product["variants"]
            disc["in_stock"] = True if self.get_inventory_quantity(variants) > 0 else False
            disc["price"] = self.get_price_from_variant(variants[0])
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = self.get_flight_spec(response.json()["metafields"])

            yield disc
        except Exception as e:
            self.logger.error(f"Error parsing disc: {product['title']}({self.create_product_url(product['handle'])})")
            self.logger.error(e)

    def clean_products(self, products):
        self.logger.debug(f"Cleaning {len(products)} products")

        # Remove products with no variants
        products = [product for product in products if len(product["variants"]) > 0]

        # Remove products with discsjappa as vendor. These are used discs
        products = [product for product in products if product["vendor"] != "Discsjappa"]

        # Remove products that has wrong product type
        allowed_product_types = ["Putt og Approach", "Midrange", "Fairway driver", "Distance driver"]
        products = [product for product in products if product["product_type"] in allowed_product_types]

        self.logger.debug(f"Cleaned products: {len(products)}")

        return products

    def create_product_url(self, product_handle: str):
        return f"https://discsjappa.no/products/{product_handle}"

    def get_inventory_quantity(self, variants) -> float:
        return sum([float(variant["inventory_quantity"]) for variant in variants])

    def get_price_from_variant(self, variant) -> float:
        return float(variant["price"])

    def get_flight_spec(self, metafields) -> tuple:
        speed = glide = turn = fade = None

        for metafield in metafields:
            if metafield["key"] == "first_number":    #speed
                speed = float(metafield["value"])
            elif metafield["key"] == "second_number": #glide
                glide = float(metafield["value"])
            elif metafield["key"] == "third_number":  #turn
                turn = float(metafield["value"])
            elif metafield["key"] == "fourth_number": #fade
                fade = float(metafield["value"])

        # Raise exception if any of the flight spec values are missing
        has_none_values = all(value is None for value in (speed, glide, turn, fade))
        self.logger.debug(f"Has none values: {has_none_values}")

        if has_none_values:
            raise Exception(f"Missing flight spec values: (speed, glide, turn, fade) = {speed, glide, turn, fade}")

        return speed, glide, turn, fade