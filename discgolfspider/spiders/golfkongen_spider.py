import re
import traceback
from base64 import b64encode
from typing import List
from urllib.parse import urlencode

import scrapy

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem


class GolfkongenSpider(scrapy.Spider):
    name = "golfkongen"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.base_url = "https://api.quickbutik.com/v1"
        self.query_params = {"limit": 100, "offset": 0, "include_details": "true"}
        self.token = settings["GOLFKONGEN_API_KEY"]

        if not self.token:
            self.logger.error("No token found for golfkongen.no")
            return

        # Encode to base64 strig
        username_password = f"{self.token}:{self.token}".encode()
        encoded_token = b64encode(username_password).decode()

        self.headers = {"Authorization": f"Basic {encoded_token}"}

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

        product_count = len(products)
        if product_count == 0:
            self.logger.error("No products found for golfkongen.no")
            return

        # Remove unwanted products
        products = self.clean_products(products)

        # Parse products
        for product in products:
            disc = CreateDiscItem()

            try:
                brand = self.find_brand(product)
                disc["brand"] = brand
                disc["name"] = self.clean_name(product["title"])
                disc["spider_name"] = self.name
                disc["retailer"] = "golfkongen.no"

                url = product["url"]
                disc["url"] = url
                disc["retailer_id"] = create_retailer_id(disc["brand"], url)
                disc["image"] = self.get_first_image(product["images"])
                disc["in_stock"] = self.is_product_in_stock(product)
                disc["price"] = int(product["price"].split(".")[0])
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = self.get_flight_specs(product["description"])

                yield disc
            except Exception as e:
                self.logger.error(f"Error parsing disc: {disc}, reason: {e}: {traceback.print_exc()}")

        # When downloaded prdocuts is equal to limit, there are more products to download
        if product_count == self.query_params["limit"]:
            self.query_params["offset"] += self.query_params["limit"]
            params = urlencode(self.query_params)
            url = f"{self.base_url}/products?{params}"

            yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def clean_products(self, products) -> list:
        products = [product for product in products if self.is_disc_product(product)]

        return products

    def is_disc_product(self, product: dict) -> bool:
        if "categories" not in product:
            return False

        head_category: str = product["headcategory_name"]
        is_accessory: bool = self.find_category(product["categories"], "tilbehør")
        is_bag: bool = self.find_category(product["categories"], "bager og sekker")
        is_set: bool = self.find_category(product["categories"], "discgolf sett")

        return head_category.lower() == "discgolf" and not is_accessory and not is_bag and not is_set

    def find_category(self, categories: list, target: str) -> bool:
        for category_list in categories:
            for category in category_list:
                if "category" not in category:
                    continue

                if category["category"].lower() == target:
                    return True

        return False

    def clean_name(self, name: str) -> str:
        unwanted_words = ["putter", "midrange", "driver", "distance", "fairway", "putt"]
        name = name.lower()

        for word in unwanted_words:
            if word in name:
                name = name.split(word)[0].rstrip()

        return name.title()

    def find_brand(self, product: dict) -> str | None:
        exclude = ["putter", "midrange", "driver", "distance driver", "tilbehør"]
        categories = [category_list for category_list in product["categories"] if len(category_list) >= 2]

        for category_list in categories:
            self.logger.debug(f" Current list: {category_list}")

            for i, category in enumerate(category_list):
                category_name = category["category"].lower()
                self.logger.debug(f"i: {i}, category: {category_name}")
                next_category_name = category_list[i + 1]["category"].lower()

                if category_name == "discgolf" and next_category_name not in exclude:
                    self.logger.debug(f"Found brand: {next_category_name}")

                    # Fix for latitude 64
                    if next_category_name == "latitude64":
                        next_category_name = "latitude 64"
                    elif next_category_name == "mvp/axiom":
                        disc_name = product["title"].lower()
                        next_category_name = "mvp" if "mvp" in disc_name else "axiom"

                    return next_category_name
                else:
                    break

        return None

    def get_first_image(self, images: dict) -> str:
        if len(images) == 0 and "1" not in images:
            raise Exception("No images found")

        # Find the key of the first element and the return the value
        first_key = list(images.keys())[0]
        return images[first_key]["image"]

    def is_product_in_stock(self, product: dict) -> bool:
        quantity = 0
        variants: list = product.get("variants")

        if variants and len(variants) > 0:
            for variant in variants:
                qty_value = variant.get("qty")
                quantity += int(qty_value) if qty_value else 0
        else:
            qty_value = product.get("qty")
            quantity = int(qty_value) if qty_value else 0

        return quantity > 0

    def get_flight_specs(self, description: str) -> List[float]:
        output_dict = {"Speed": None, "Glide": None, "Turn": None, "Fade": None}

        # Look for each rating in the text using regular expressions
        for key in output_dict.keys():
            # Find number with optional sign and optional comma value
            match = re.search(rf"{key}:\s*([-+]?(?:\d*\,*\d+))", description)
            if match:
                try:
                    value = float(match.group(1).replace(",", "."))
                    output_dict[key] = value
                except ValueError:
                    output_dict[key] = None

        return list(output_dict.values())

    def get_flight_spec(self, spec: str, description: str) -> float:
        spec = spec.lower() + ":"

        if spec not in description:
            raise Exception(f"Could not find flight spec ({spec}) in description")

        spec_value: str = description.split(spec)[1].split("</span>")[0].strip().replace(",", ".")
        value = float(spec_value)

        return value
