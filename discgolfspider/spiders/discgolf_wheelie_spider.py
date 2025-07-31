import re
import time

import scrapy

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem


class DiscgolfWheelieSpider(scrapy.Spider):
    name = "discgolf_wheelie"
    url = "discgolf-wheelie.no"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.baseUrl = "https://45ed2d.myshopify.com/admin/api/2024-01"
        self.token = settings["DISCGOLFWHEELIE_API_KEY"]

        if not self.token:
            self.logger.error(f"No token found for {self.url}")
            return

        self.headers = {"X-Shopify-Access-Token": self.token}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    async def start(self):
        url = f"{self.baseUrl}/products.json?status=active&product_type=Disk&limit=100"
        yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        products = response.json()["products"]

        if len(products) == 0:
            self.logger.error("No products found for ")
            return

        # Remove unwanted products
        products = self.clean_products(products)

        for product in products:
            self.logger.debug(f"Product: {product['title']}")

            try:
                time.sleep(0.5)  # Sleep to avoid rate limit

                disc = CreateDiscItem()
                disc["name"] = product["title"]
                disc["spider_name"] = self.name
                disc["brand"] = product["vendor"]
                disc["retailer"] = self.url
                disc["url"] = self.create_product_url(product["handle"])
                disc["retailer_id"] = create_retailer_id(disc["brand"], disc["url"])

                image = product["image"]
                disc["image"] = image["src"] if image else "https://via.placeholder.com/300"

                variants = product["variants"]
                disc["in_stock"] = True if self.get_inventory_quantity(variants) > 0 else False
                disc["price"] = self.get_price_from_variant(variants[0])

                disc["speed"] = self.get_flight_spec_from_tag("Speed", product["tags"])
                disc["glide"] = self.get_flight_spec_from_tag("Glide", product["tags"])
                disc["turn"] = self.get_flight_spec_from_tag("Turn", product["tags"])
                disc["fade"] = self.get_flight_spec_from_tag("Fade", product["tags"])

                if any([disc["speed"], disc["glide"], disc["turn"], disc["fade"]]) is None:
                    raise ValueError(
                        f"Missing flight spec values: {disc['speed']}, {disc['glide']}, {disc['turn']}, {disc['fade']}"
                    )

                yield disc
            except Exception as e:
                self.logger.error(
                    f"Error parsing disc: {product['title']}({self.create_product_url(product['handle'])})"
                )
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

        self.logger.debug(f"Cleaned products: {len(products)}")

        return products

    def create_product_url(self, product_handle: str):
        return f"https://{self.url}/products/{product_handle}"

    def get_inventory_quantity(self, variants) -> float:
        return sum([float(variant["inventory_quantity"]) for variant in variants])

    def get_price_from_variant(self, variant) -> float:
        return float(variant["price"])

    def get_flight_spec_from_tag(self, flight_spec: str, tags: str) -> float | None:
        match = re.search(rf"{flight_spec} (-?\d+(\.\d+)?)", tags)

        return float(match.group(1)) if match else None
