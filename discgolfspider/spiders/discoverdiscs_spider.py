import scrapy

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem


class DiscoverdiscsSpider(scrapy.Spider):
    name = "discoverdiscs"
    allowed_domains = ["discoverdiscs.no"]
    start_urls = ["https://discoverdiscs.no"]

    def parse(self, response):
        brands = response.css('div[id="childlink-Merker"] > ul > li')

        for brand in brands:
            brand_name = brand.css("a::text").get().strip()
            next_page = brand.css("a::attr(href)").get()

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        products = response.css("li.grid__item")

        for product in products:
            disc = CreateDiscItem()

            try:
                name = product.css("span.card-information__text::text").get().replace("\n", "").strip()
                disc["name"] = name

                url = product.css("a").attrib["href"]
                url = f"{self.start_urls[0]}{url}"
                disc["url"] = url
                disc["retailer_id"] = create_retailer_id(brand, url)

                if self.is_backpack(name, url):
                    self.logger.debug(f"Skipping backpack: {disc}")
                    continue

                disc["image"] = product.css("img").attrib["src"]
                disc["spider_name"] = self.name

                badge_text = product.css(".badge::text").get()
                disc["in_stock"] = True if badge_text != "Utsolgt" else False
                disc["retailer"] = self.allowed_domains[0]
                disc["brand"] = brand
                disc["price"] = self.parse_price(product)

                flight_specs = self.parse_flight_spec(product)
                if any(flight_spec is None for flight_spec in flight_specs):
                    self.logger.warning(f"{disc} is missing flight spec data. {flight_specs=} ")

                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs

                yield disc
            except Exception as e:
                self.logger.error(f"Error parsing disc: {disc}: {e})")

        next_page = response.css("a.pagination__item--prev::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})

    def parse_flight_spec(self, product) -> tuple:
        speed = glide = turn = fade = None
        flight_specs = product.css(".disc-info__value::text").getall()

        if flight_specs and len(flight_specs) == 4:
            speed, glide, turn, fade = [float(spec) for spec in flight_specs]

        return speed, glide, turn, fade

    def is_backpack(self, name, url):
        url_contains = "bag" in url or "backpack" in url
        name_contains = "bag" in name.lower() or "backpack" in name.lower()

        return url_contains or name_contains

    def parse_price(self, product) -> int:
        price = -1
        prices = product.css(".price-item::text").getall()
        prices = [self.format_price(price) for price in prices]
        prices = [price for price in prices if price != ""]

        if prices:
            price = int(prices[1])

        return price

    def format_price(self, price: str) -> str:
        price_formatted = price.replace("\n", "").replace("Fra", "").strip()

        if "," in price_formatted:
            price_formatted = price_formatted.split(",")[0]

        return price_formatted
