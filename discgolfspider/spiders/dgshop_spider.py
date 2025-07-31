from typing import List

import scrapy

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem


class   DgshopSpider(scrapy.Spider):
    name = "dgshop"
    allowed_domains = ["dgshop.no"]
    start_urls = ["https://www.dgshop.no/"]

    def parse(self, response):
        brands = response.xpath("/html/body/div[2]/div[1]/div/div[2]/nav/ul/li[2]/ul/li")
        for brand in brands:
            brand_name = brand.css("a > span::text").get()
            next_page = brand.css("a::attr(href)").get()

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        for product in response.css(".product-item-info"):
            disc = CreateDiscItem()

            try:
                disc_name = product.css(".product-item-link::text").get()
                disc["name"] = disc_name.replace("\r", "").replace("\n", "").strip()
                disc["image"] = product.css(".product-image-photo::attr(src)").get()

                if not self.valid_disc_name(disc["name"]):
                    continue

                url = product.css("a::attr(href)").get()
                disc["url"] = url
                disc["spider_name"] = self.name
                disc["in_stock"] = True
                disc["retailer"] = self.allowed_domains[0]
                disc["retailer_id"] = create_retailer_id(brand, url)
                disc["brand"] = brand

                price = product.css(".price::text").get()
                if price:
                    disc["price"] = int("".join(filter(str.isdigit, price)))

                flight_specs_raw = product.css(".flight-rating > text::text").getall()
                flight_specs = self.get_flight_specs(flight_specs_raw)
                if None in flight_specs:
                    self.logger.warning(f"{disc['name']}({disc['url']}) is missing flight spec data. {flight_specs=} ")
                    disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [None, None, None, None]
                else:
                    disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs

                yield disc
            except Exception as e:
                self.logger.error(f"Error parsing disc: {disc['name']}({disc['url']}). Reason: {e}")

        next_page = response.css("li.pages-item-next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})

    def valid_disc_name(self, disc_name: str) -> bool:
        if not disc_name:
            return False

        bad_words = ["startsett", "starter set", "battle pack"]
        for bad_word in bad_words:
            if bad_word in disc_name.lower():
                return False

        return True

    def get_flight_specs(self, flight_specs) -> List[float]:
        if not flight_specs:
            return [None, None, None, None]

        parsed = [float(numeric_string.replace(",", ".")) for numeric_string in flight_specs]
        return parsed
