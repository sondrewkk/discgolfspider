from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy


class ProdiscSpider(scrapy.Spider):
    name = "prodisc"
    allowed_domains = ["prodisc.no"]
    start_urls = ["https://www.prodisc.no"]

    def parse(self, response):
        brands = response.css("ul[id=\"HeaderMenu-MenuList-3\"] > li")

        for brand in brands:
            brand_name = brand.css("a::text").get().strip()
            link_url = brand.css("a::attr(href)").get()
            next_page = f"{self.start_urls[0]}{link_url}"

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        products = response.css("ul[id=\"product-grid\"] > li")

        for product in products:
            disc = CreateDiscItem()
            disc["name"] = product.css("h3.card-information__text > a::text").get().replace("\n", "").strip()
            disc["image"] = product.css("img").attrib["src"]
            disc["spider_name"] = self.name
            disc["retailer"] = self.allowed_domains[0]
            disc["brand"] = brand 

            badge = product.css("span.badge::text").get()
            disc["in_stock"] = True if badge is None or badge != "Utsolgt" else False

            url = product.css("a").attrib["href"]
            disc["url"] = f"{self.start_urls[0]}{url}"
            disc["retailer_id"] = create_retailer_id(brand, url)

            prices = product.css(".price-item::text").getall()
            prices = [price.strip().replace("\n", "") for price in prices]
            prices = [price for price in prices if price != ""]
            disc["price"] = int(prices[len(prices) - 1].split(",")[0])

            flight_specs = product.css("div[class*=\"flightbox-\"]::text").getall()
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [float(spec) for spec in flight_specs]

            current_brand = product.css("div.caption-with-letter-spacing::text").get()
            if current_brand:
                current_brand = current_brand.split(" ")[0]

            # A measurement to fix the issue where latitude and westside discs is also in dynamic disc brand category
            if current_brand in brand:
                yield disc

        next_page = response.css("a.pagination__item--prev::attr(href)").get()
        if next_page is not None:
             yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
