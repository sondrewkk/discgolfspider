import re
import time

import scrapy

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.helpers.shopify import calculate_sleep_duration
from discgolfspider.items import CreateDiscItem


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

        self.headers = {"X-Shopify-Access-Token": self.token}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def start_requests(self):
        url = f"{self.baseUrl}/products.json?status=active&limit=100"
        yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        products = response.json()["products"]

        if len(products) == 0:
            self.logger.error(f"No products found for {self.retailer}")
            return

        # Remove unwanted products
        products = self.clean_products(products)

        for product in products:
            url = f"{self.baseUrl}/products/{product['id']}/metafields.json"
            yield scrapy.Request(
                url, headers=self.headers, callback=self.parse_product_with_metafields, cb_kwargs={"product": product}
            )

        # Check if response containt next link header and follow it if it does
        if "link" in response.headers:
            links = response.headers["link"].decode("utf-8")
            next_link_match = re.search('<([^>]+)>; rel="next"', links)

            if next_link_match:
                next_link = next_link_match.group(1)
                yield scrapy.Request(next_link, headers=self.headers, callback=self.parse)

    def parse_product_with_metafields(self, response, product):
        self.logger.debug(f"Product: {product['title']}")

        sleep_duration = calculate_sleep_duration(response)
        time.sleep(sleep_duration)  # Sleep to avoid rate limit

        disc = CreateDiscItem()
        disc["name"] = product["title"]
        disc["url"] = self.create_product_url(product["handle"])

        try:
            disc["spider_name"] = self.name
            disc["brand"] = product["vendor"]
            disc["retailer"] = self.retailer
            disc["retailer_id"] = create_retailer_id(disc["brand"], disc["url"])
            disc["image"] = product["image"]["src"]

            variants = product["variants"]
            disc["in_stock"] = self.get_inventory_quantity(variants) > 0
            disc["price"] = self.get_price_from_variant(variants[0])
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = self.get_flight_spec(
                response.json()["metafields"]
            )

            yield disc
        except Exception as e:
            self.logger.error(f"Error parsing disc: {disc})")
            self.logger.error(e)

    def clean_products(self, products):
        self.logger.debug(f"Cleaning {len(products)} products")

        # Remove products with no variants
        products = [product for product in products if len(product["variants"]) > 0]

        # Remove if product if it contains unwanted words
        word_blacklist = ["pakke", "sekk", "tilbehør", "håndkle"]
        products = [
            product for product in products if not any(word in product["tags"].lower() for word in word_blacklist)
        ]

        self.logger.debug(f"Cleaned products: {len(products)}")

        return products

    def create_product_url(self, product_handle: str):
        return f"https://{self.retailer}/products/{product_handle}"

    def get_inventory_quantity(self, variants) -> float:
        return sum([float(variant["inventory_quantity"]) for variant in variants])

    def get_price_from_variant(self, variant) -> float:
        return float(variant["price"])

    def get_flight_spec(self, metafields: list[dict[str, int | str]]) -> tuple:
        speed = glide = turn = fade = None
        valid_flight_spec_keys = ["speed", "glide", "turn", "fade"]
        metafields = [metafield for metafield in metafields if metafield["key"] in valid_flight_spec_keys]

        self.logger.debug(f"Metafields: {metafields}")

        for metafield in metafields:
            if metafield["key"] == "speed":
                speed = self.get_flight_spec_value(metafield)
            elif metafield["key"] == "glide":
                glide = self.get_flight_spec_value(metafield)
            elif metafield["key"] == "turn":
                turn = self.get_flight_spec_value(metafield)
            elif metafield["key"] == "fade":
                fade = self.get_flight_spec_value(metafield)

        # Raise exception if any of the flight spec values are missing
        has_none_values = all(value is None for value in (speed, glide, turn, fade))  #
        self.logger.debug(f"Has none values: {has_none_values}")

        if has_none_values:
            # Can be change to raise exception when data from retailer is more reliable
            self.logger.debug(f"Missing flight spec values: (speed, glide, turn, fade) = {speed, glide, turn, fade}")

        return speed, glide, turn, fade

    def get_flight_spec_value(self, metafield: dict) -> float:
        value = metafield["value"]

        if isinstance(value, str):
            value = value.replace(",", ".")

        return float(value)
