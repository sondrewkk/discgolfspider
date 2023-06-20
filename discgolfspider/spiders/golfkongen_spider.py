from discgolfspider.items import CreateDiscItem
from discgolfspider.helpers.retailer_id import create_retailer_id
from base64 import b64encode
from urllib.parse import urlencode
from pprint import pprint
from typing import Tuple

import scrapy


class GolfkongenSpider(scrapy.Spider):
    name = "golfkongen"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.base_url = "https://api.quickbutik.com/v1"
        self.query_params = {
            "limit": 100,
            "offset": 0,
            "include_details": "true"
        }
        self.token = settings["GOLFKONGEN_API_KEY"]

        if not self.token:
            self.logger.error("No token found for golfkongen.no")
            return

        # Encode to base64 strig
        username_password = f"{self.token}:{self.token}".encode()
        encoded_token = b64encode(username_password).decode()

        self.headers = {
            "Authorization": f"Basic {encoded_token}"
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def start_requests(self):
        params = urlencode(self.query_params)
        url = f"{self.base_url}/products?{params}"

        self.logger.debug(f"Requesting: {url}")

        yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        products = response.json()

        if product_count := len(products) == 0:
            self.logger.error("No products found for golfkongen.no")
            return

        # Remove unwanted products
        products = self.clean_products(products)

        # Parse products
        self.parse_products(products)

        # When downloaded prdocuts is equal to limit, there are more products to download
        if product_count == self.query_params["limit"]:
            self.query_params["offset"] += self.query_params["limit"]
            params = urlencode(self.query_params)
            url = f"{self.base_url}/products?{params}"

            yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_products(self, products):
        for product in products:
            try:
                #self.logger.debug(f"{product['title']}")

                disc = CreateDiscItem()
                disc["name"] = self.clean_name(product["title"])
                disc["spider_name"] = self.name
                disc["retailer"] = "golfkongen.no"

                brand = self.find_brand(product)  # TODO: Parse brand
                disc["brand"] = brand

                url = product["url"]
                disc["url"] = url
                disc["retailer_id"] = create_retailer_id(disc["brand"], url)
                disc["image"] = self.get_first_image(product["images"])
                disc["in_stock"] = self.is_product_in_stock(product)
                disc["price"] = int(product["price"])
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = self.get_flight_specs(product["description"])
                self.logger.debug(f"name: {disc['name']}")

                # yield disc
            except Exception as e:
                # self.logger.error(f"Error parsing disc: {product['title']}({self.create_product_url(product['handle'])})")
                self.logger.error(e)

    def clean_products(self, products) -> list:
        self.logger.debug(f"Cleaning {len(products)} products")
        products = [product for product in products if self.is_discgolf_product(product)]

        return products

    def clean_name(self, name: str) -> str:
        unwanted_words = ["putter", "midrange", "driver", "distance", "fairway", "putt"]
        name = name.lower()

        for word in unwanted_words:
            if word in name:
                name = name.split(word)[0].rstrip()

        return name.title()

    def is_discgolf_product(self, product: dict) -> bool:
        head_category: str = product["headcategory_name"].lower()
        return True if head_category == "discgolf" else False

    def find_brand(self, product: dict) -> str:
        exclude = ["putter", "midrange", "driver"]
        categories = [category_list for category_list in product["categories"] if category_list["category"].lower() == "discgolf"]
        
        pprint(categories)

        

        for category_list in categories:
        if len(category_list) > 2 and all(category['category'] != exclude for category in category_list):
            return category_list
    return None

    def get_first_image(self, images: dict) -> str:
        if len(images) == 0 and "1" not in images:
            raise Exception("No images found")

        return images["1"]["image"]

    def is_product_in_stock(self, product: dict) -> bool:
        quantity = 0
        if "variants" in product and len(product["variants"]) > 0:
            quantity = sum(int(variant["qty"]) for variant in product["variants"])
        else:
            quantity = int(product.get("qty", 0))

        return quantity > 0

    def get_flight_specs(self, description: str) -> Tuple[float, float, float, float]:
        flight_spec_names = ["speed", "glide", "turn", "fade"]
        description = description.lower()
        flight_specs = {key: self.get_flight_spec(key, description) for key in flight_spec_names}

        return tuple(flight_specs.values())

    def get_flight_spec(self, spec: str, description: str) -> float:
        spec = spec.lower() + ":"

        if spec not in description:
            raise Exception(f"Could not find flight spec ({spec}) in description")

        spec_value: str = description.split(spec)[1].split("</span>")[0].strip().replace(",", ".")
        value = float(spec_value)

        return value
