from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy


class StarframeSpider(scrapy.Spider):
    name = "starframe"
    allowed_domains = ["starframe.no"]
    start_urls = ["https://www.starframe.no/categories/typer"]

    def parse(self, response):
        products = response.css(".product-box-wrapper")

        for product in products:
            disc = CreateDiscItem()
            disc["name"] = product.css(".title::text").get().strip()
            disc["image"] = product.css(".image-mainimage > img").attrib["src"]
            disc["spider_name"] = self.name
            disc["retailer"] = self.allowed_domains[0]
            disc["price"] = int(product.css(".price::text").get().strip().replace(",-", ""))
            disc["in_stock"] = True

            brand = product.css(".manufacturers::text").get().strip()
            disc["brand"] = brand
           
            url = product.css('.__product_url').attrib["href"]
            disc["url"] = url

            disc["retailer_id"] = create_retailer_id(brand, url)

            flight_specs = product.css('.product_box_tag > span::text').getall()
            flight_specs = [float(spec) for spec in flight_specs]
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs

        # for brand in brands:
        #     brand_name = brand.css("a::text").get().strip()
        #     link_url = brand.css("a::attr(href)").get()
        #     next_page = f"{self.start_urls[0]}{link_url}"

        #     if next_page is not None:
        #         yield response.follow(
        #             next_page,
        #             callback=self.parse_products,
        #             cb_kwargs={"brand": brand_name},
        #         )

    # def parse_products(self, response, brand):
    #     products = response.css("ul[id=\"product-grid\"] > li")

    #     for product in products:
    #         disc = CreateDiscItem()
    #         disc["name"] = product.css("h3.card-information__text > a::text").get().replace("\n", "").strip()
    #         disc["image"] = product.css("img").attrib["src"]
    #         disc["spider_name"] = self.name
    #         disc["retailer"] = self.allowed_domains[0]
    #         disc["brand"] = brand 

    #         badge = product.css("span.badge::text").get()
    #         disc["in_stock"] = True if badge is None or badge != "Utsolgt" else False
    #         url = product.css("a").attrib["href"]
    #         url = f"{self.start_urls[0]}{url}"
    #         disc["url"] = url
    #         disc["retailer_id"] = create_retailer_id(brand, url)

    #         prices = product.css(".price-item::text").getall()
    #         prices = [price.strip().replace("\n", "").replace(".", "") for price in prices]
    #         prices = [price for price in prices if price != ""]
    #         disc["price"] = int(prices[len(prices) - 1].split(",")[0])

    #         flight_specs = product.css("div[class*=\"flightbox-\"]::text").getall()
    #         if flight_specs:
    #             disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [float(spec.replace(",", ".")) for spec in flight_specs]
    #         else:
    #             self.logger.warning(f"{disc['name']}({disc['url']}) is missing flight spec data. {flight_specs=} ")
    #            

    #         current_brand = product.css("div.caption-with-letter-spacing::text").get()
    #         if current_brand:
    #             current_brand = current_brand.split(" ")[0]

    #         # A measurement to fix the issue where latitude and westside discs is also in dynamic disc brand category
    #         if current_brand in brand:
    #             yield disc

    #     next_page = response.css("a.pagination__item--prev::attr(href)").get()
    #     if next_page is not None:
    #          yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
