from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy


class DiscgolfdynastySpider(scrapy.Spider):
    name = "discgolfdynasty"
    allowed_domains = ["discgolfdynasty.no"]
    start_urls = ["https://www.discgolfdynasty.no"]

    def parse(self, response):
        brands = response.xpath("/html/body/div[1]/nav/div/ul[2]/li[2]/ul/li")

        for brand in brands:
            brand_path = brand.css("a::attr(href)").get()
            brand_name = brand.css("a::text").get().strip()

            next_page = f"{self.start_urls[0]}{brand_path}"

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        for product in response.css(".product-grid-item"):
            disc = CreateDiscItem()
            disc["name"] = product.css("p::text").get().split(" ", 1)[1]
            disc["image"] = product.css("img::attr(src)").get()
            disc["spider_name"] = self.name
            disc["brand"] = brand
            disc["retailer"] = self.allowed_domains[0]
            disc["price"] = int(product.css("small::text").get())

            sold_out = product.css(".badge--sold-out").get()
            disc["in_stock"] = True if not sold_out else False

            url = product.css("a::attr(href)").get()
            disc["url"] = f"{self.start_urls[0]}{url}"
            disc["retailer_id"] = create_retailer_id(brand, url)

            if not disc["image"]:
                disc["image"] = "https://via.placeholder.com/300"

            yield response.follow(
                disc["url"],
                callback=self.parse_product_details,
                cb_kwargs={"disc": disc},
            )

        next_page = response.css(".pagination-custom a[title='Neste »']::attr(href)").get()

        if next_page is not None:
            next_page = f"{self.start_urls[0]}{next_page}"
            yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})

    def parse_product_details(self, response, disc):
        flight_specs = response.css(".product-description ul li::text").getall()

        if flight_specs:
            flight_specs = flight_specs[:4]
            flight_specs = [self.format_flight_spec(numeric_string) for numeric_string in flight_specs]
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs
        else:
            self.logger.warning(f"{disc['name']}({disc['url']}) is missing flight spec data. {flight_specs=} ")
            disc["speed"], disc["glide"], disc["turn"] ,disc["fade"] = [None, None, None, None]

        yield disc

    def format_flight_spec(self, flight_spec) -> float:
        return float(flight_spec.split(":")[1].strip())
