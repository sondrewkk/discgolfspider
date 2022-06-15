from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy


class ProdiscSpider(scrapy.Spider):
    name = "prodisc"
    allowed_domains = ["prodisc.no"]
    start_urls = ["https://prodisc.no"]

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
            prices = [price.strip().replace("\n", "").replace(".", "") for price in prices]
            prices = [price for price in prices if price != ""]
            disc["price"] = int(prices[len(prices) - 1].split(",")[0])

            flight_specs = product.css("div[class*=\"flightbox-\"]::text").getall()
            if flight_specs:
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [float(spec.replace(",", ".")) for spec in flight_specs]
            else:
                self.logger.warning(f"{disc['name']}({disc['url']}) is missing flight spec data. {flight_specs=} ")
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [None, None, None, None]

            current_brand = product.css("div.caption-with-letter-spacing::text").get()
            if current_brand:
                current_brand = current_brand.split(" ")[0]

            # A measurement to fix the issue where latitude and westside discs is also in dynamic disc brand category
            if current_brand in brand:
                yield disc

        next_page = response.css("a.pagination__item--prev::attr(href)").get()
        if next_page is not None:
             yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})

# Ser ut til at disker som er lagret som in stock = False ikke klarer å skifte status til in stock = True
# Diskene for prodisk prøver først å legge til disken fordi den tror den ikke eksisterer fra før,
# deretter prøver den å oppdatere disken men finner ingen forskjeller... Burde ha instock forskjellig.