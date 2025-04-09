import scrapy

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem


class AceshopSpider(scrapy.Spider):
    name = "aceshop"
    allowed_domains = ["aceshop.no"]
    start_urls = ["https://aceshop.no/categories/discer"]

    def parse(self, response):
        for product in response.css(".product-box-wrapper"):
            try:
                disc = CreateDiscItem()
                disc["name"] = product.css(".product_box_title_row a::text").get()

                if disc["name"] in "Startpakke":
                    return

                disc["image"] = product.css(".image img::attr(src)").get()

                url = product.css(".product_box_title_row a::attr(href)").get()
                disc["url"] = url
                disc["spider_name"] = self.name
                disc["in_stock"] = int(product.css(".product::attr(data-quantity)").get()) > 0
                disc["retailer"] = self.allowed_domains[0]

                brand = product.css(".product::attr(data-manufacturer)").get().strip().title()
                if not brand:
                    raise ValueError(f"Could not find brand for disc: {disc}")
                elif brand.lower() == "dgputt":
                    self.logger.debug(f"Skipping disc from brand {brand}")
                    continue

                disc["retailer_id"] = create_retailer_id(brand, url)
                disc["brand"] = brand

                price = int(product.css(".product-box::attr(data-price-including-tax)").get())
                if price:
                    disc["price"] = price / 100

                flight_specs = self.parse_flight_specs(product.css(".product_box_tag span::text").getall())

                if any(spec is None for spec in flight_specs):
                    self.logger.warning(f"Could not parse flight specs for {disc}")
                else:
                    disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs

                yield disc
            except Exception as e:
                self.logger.error(f"Error parsing disc: {e}")

        next_page = response.css(".paginator_link_next::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_flight_specs(self, flight_specs):
        speed = glide = turn = fade = None

        if len(flight_specs) == 4:
            flight_specs = [float(numeric_string.replace(".", "").replace(",", ".")) for numeric_string in flight_specs]
            speed, glide, turn, fade = flight_specs

        return speed, glide, turn, fade
