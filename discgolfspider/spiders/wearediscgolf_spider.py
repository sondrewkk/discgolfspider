import scrapy
from scrapy import Request
from scrapy.http import Headers

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem


class WeAreDiscgolfSpider(scrapy.Spider):
    name = "wearediscgolf"
    allowed_domains = ["wearediscgolf.no"]
    start_urls = ["https://wearediscgolf.no/wp-json/wc/v3/products?per_page=100&page=1"]
    http_auth_domain = "wearediscgolf.no"
    image_placeholder = "https://wearediscgolf.no/content/uploads/woocommerce-placeholder-600x600.png"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.http_user = settings["WEAREDISCGOLF_API_KEY"]
        self.http_pass = settings["WEAREDISCGOLF_API_SECRET"]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def parse(self, response):
        products = response.json()
        disc_products = self.clean_products(products)

        for disc_product in disc_products:
            try:
                disc = CreateDiscItem()
                disc["name"] = disc_product["name"]

                num_of_images = len(disc_product["images"])
                image_url = disc_product["images"][0]["src"] if num_of_images > 0 else self.image_placeholder
                disc["image"] = image_url

                in_stock = True if disc_product["stock_status"] == "instock" else False
                disc["in_stock"] = in_stock

                url = disc_product["permalink"]
                disc["url"] = url
                disc["spider_name"] = self.name

                attributes = disc_product["attributes"]
                brand = self.get_attribute(attributes, "Produsent")
                disc["brand"] = brand
                disc["retailer"] = self.allowed_domains[0]
                disc["retailer_id"] = create_retailer_id(brand, url)

                flight_specs = self.parse_flight_spec(attributes)
                if None in flight_specs and in_stock:
                    self.logger.warning(f"{disc['name']}({disc['url']}) is missing flight spec data. {flight_specs=} ")

                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs

                price = self.calculate_price(disc_product["price"], disc_product["tax_status"], in_stock)
                disc["price"] = price

                yield disc
            except Exception as e:
                name = disc_product["name"]
                link = disc_product["permalink"]
                self.logger.error(f"Error parsing disc: {name}({link}). Reason: {e}")

        # Check for next page
        headers: Headers = response.headers
        next_page = self.get_next_page(headers)

        if next_page is not None:
            yield Request(next_page, callback=self.parse)

    def clean_products(self, products: list) -> list:
        return [
            product
            for product in products
            if self.is_disc(product)
            and product["status"] == "publish"
            and product["stock_status"] == "instock"
            and not product["slug"].endswith("mini")
        ]

    def is_disc(self, product: dict) -> bool:
        product_type: str = product["categories"][0]["slug"]
        return product_type == "golfdiscer"

    def get_next_page(self, headers: Headers) -> str:
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

    def get_attribute(self, attributes: list, value: str) -> str:
        attribute = next((attr for attr in attributes if attr["name"] == value), None)

        if not attribute:
            self.logger.debug(f"Could not find attribute: {value}")
            return None

        if len(attribute["options"]) == 0:
            self.logger.debug(f"attribute ({value} has no value")
            return None

        return attribute["options"][0]

    def parse_flight_spec(self, attributes: list) -> list:
        spec_types = ["Speed", "Glide", "Turn", "Fade"]
        flight_specs = []

        for spec_type in spec_types:
            spec = self.get_attribute(attributes, spec_type)

            if spec:
                # Handle edge case for turn, when turn has a number before minus
                if spec_type == "Turn" and self.is_wrong_turn_format(spec):
                    self.logger.debug(f"Wrong turn format: {spec}")
                    spec = spec.split("-")[0]
                    spec = spec.replace(",", ".")
                    spec = f"-{spec}"
                else:
                    spec = spec.replace(",", ".")

            try:
                spec = float(spec)
            except Exception as e:
                msg = self.logger.error(f"Error parsing flight spec: {spec_type}({spec}). Reason: {e}")
                raise ValueError(msg) from e

            flight_specs.append(spec)

        return flight_specs

    def is_wrong_turn_format(self, value: str) -> bool:
        wrong_format = False
        minus_index = value.find("-")

        if minus_index > -1 and not minus_index == 0:
            wrong_format = True

        return wrong_format

    def calculate_price(self, price: str, tax_status: str, in_stock: bool) -> float:
        if price and in_stock:
            calculated_price = float(price)

            if tax_status == "taxable":
                calculated_price *= 1.25
        else:
            calculated_price = -9999.0
            self.logger.debug(f"Price is not set or disc is out of stock. {price=} {tax_status=} {in_stock=}")

        return calculated_price
