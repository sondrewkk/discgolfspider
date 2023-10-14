from typing import Optional
from scrapy.http import Headers
from scrapy import Request
from discgolfspider.helpers.brand_helper import BrandHelper
from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem

import scrapy


class DiscshopenSpider(scrapy.Spider):
    name = "discshopen"
    allowed_domains = ["discshopen.no"]
    start_urls = ["https://discshopen.no/wp-json/wc/v3/products?page=1&per_page=100"]
    http_auth_domain = "discshopen.no"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.http_user = settings["DISCSHOPEN_API_KEY"]
        self.http_pass = settings["DISCSHOPEN_API_SECRET"]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def parse(self, response):
        products = self.unique_dicts(response.json(), "id")
        disc_products = [product for product in products if self.is_valid_product(product)]

        for disc_product in disc_products:
            try:
                disc = CreateDiscItem()
                disc["name"] = disc_product["name"]

                image = "https://discshopen.no/wp-content/uploads/woocommerce-placeholder-416x416.png"
                if len(disc_product["images"]) > 0:
                    image = disc_product["images"][0]["src"]

                disc["image"] = image

                in_stock = True if disc_product["stock_status"] == "instock" else False
                disc["in_stock"] = in_stock

                url = disc_product["permalink"]
                disc["url"] = url
                disc["spider_name"] = self.name

                brand = self.get_brand_from_tags(disc_product["tags"])
                disc["brand"] = brand
                disc["retailer"] = self.allowed_domains[0]
                disc["retailer_id"] = create_retailer_id(brand, url)        # type: ignore
                flight_specs = self.get_flight_spec_from_meta_data(disc_product["meta_data"])

                if flight_specs is not None and len(flight_specs) == 4:
                    disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs
                else:
                    disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [None, None, None, None]
                    message = f"Flight specs not found for disc: {disc['name']}({url})"
                    if in_stock:
                        self.logger.warning(message)
                    else:
                        self.logger.info(message)

                price: int = -9999
                if disc_product["price"]:
                    price = int(disc_product["price"])

                disc["price"] = price

                yield disc
            except Exception as e:
                msg = f"Error parsing disc: {disc_product['name']}({disc_product['permalink']}). Reason: {e}"
                if disc_product["stock_status"] == "instock":
                    self.logger.error(msg)

        # Check for next page
        headers: Headers = response.headers
        next_page = self.get_next_page(headers)

        if next_page is not None:
            yield Request(next_page, callback=self.parse)

    def unique_dicts(self, dict_list, key):
        seen = set()
        return [seen.add(d[key]) or d for d in dict_list if d[key] not in seen]

    def is_disc(self, product: dict) -> bool:
        valid_categories = ["distance-driver", "driver", "driver-discer", "fairway-driver", "midrange", "putter"]
        categories = product["categories"] + product["tags"]
        return any(category in (category["slug"] for category in categories) for category in valid_categories)

    def is_draft(self, status: str) -> bool:
        return status == "draft"

    def get_next_page(self, headers: Headers) -> Optional[str]:
        link_header: str = headers.get("Link").decode("utf-8")
        next_page: str = None

        if not link_header:
            return None

        links = link_header.split(",")

        for link in links:
            rel = link.split(";")[1]

            # If link header is of type next
            if rel.find("next") != -1:
                next_page = link.split(";")[0].replace("<", "").replace(">", "").strip()

        return next_page

    def get_brand_from_tags(self, tags: list) -> Optional[str]:
        for tag in tags:
            name = tag["name"]
            self.logger.debug(f"Checking tag: {name}")

            brand = BrandHelper.normalize(name)
            self.logger.debug(f"Brand: {brand}")

            if brand is not None:
                return brand

        return None

    def get_flight_spec_from_meta_data(self, meta_data: list) -> list[float]:
        flight_specs_values = {"speed": 0.0, "glide": 0.0, "turn": 0.0, "fade": 0.0}

        for meta in meta_data:
            key = meta["key"].lower()

            if key in flight_specs_values:
                value = meta["value"]
                if not value:
                    raise ValueError(f"Flight spec ({key}). Value is empty")

                try:
                    value = float(meta["value"].replace(",", "."))
                    flight_specs_values[key] = value
                except Exception:
                    raise ValueError(f"Could not parse flight spec ({key}). Value: {value}")

        return list(flight_specs_values.values())

    def is_valid_product(self, product: dict) -> bool:
        return self.is_disc(product) and not self.is_draft(product["status"])
