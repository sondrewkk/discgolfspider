from ..items import CreateDiscItem

import scrapy


class GuruSpider(scrapy.Spider):
    name = "guru"
    allowed_domains = ["gurudiscgolf.no"]
    start_urls = ["https://gurudiscgolf.no/diskgolf.html"]

    def parse(self, response):
        for brand in response.css(".row.subcategories div"):
            next_page = brand.css("a::attr(href)").get(1)
            brand_name = brand.css("a::text").get(1).rstrip()

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        has_subcategories = len(response.css(".row.subcategories div").getall()) > 0

        if has_subcategories:
            for category in response.css(".row.subcategories div"):
                next_page = category.css("a::attr(href)").get()
                is_duplicated = self.is_duplicated_category(next_page)

                if next_page is not None and not is_duplicated:
                    yield response.follow(
                        next_page,
                        callback=self.parse_products,
                        cb_kwargs={"brand": brand},
                    )
        else:
            for product in response.css(".product-layout"):
                disc = CreateDiscItem()
                disc["name"] = product.css(".img-responsive::attr(alt)").get()
                disc["image"] = product.css(".img-responsive::attr(src)").get()
                disc["in_stock"] = product.css(".stock-status::text").get() != "Utsolgt"
                disc["url"] = product.css("a::attr(href)").get()
                disc["spider_name"] = self.name
                disc["retailer"] = self.allowed_domains[0]
                disc["brand"] = brand

                price = product.css(".price::text").get()
                flight_specs = product.css(".attribute-groups > span::text").getall()

                if price:
                    disc["price"] = int("".join(filter(str.isdigit, price.split(",")[0])))

                if len(flight_specs) == 4:
                    flight_specs = [
                        float(numeric_string.replace(",", ".")) for numeric_string in flight_specs
                    ]
                    (
                        disc["speed"],
                        disc["glide"],
                        disc["turn"],
                        disc["fade"],
                    ) = flight_specs
                else:
                    self.logger.warning(f"Did not find flight spec for disc with name { disc['name'] }")
                    disc["speed"] = None
                    disc["glide"] = None
                    disc["turn"] = None
                    disc["fade"] = None

                yield disc

    def is_duplicated_category(self, category_link):
        duplicated_categories = [
            "/glow",
            "/i-dye",
            "/overmold",
            "/burst",
            "/moonshine",
            "/retro",
        ]
        duplicated = any([category for category in duplicated_categories if category in category_link])

        return duplicated
