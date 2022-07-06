from discgolfspider.items import CreateDiscItem
from discgolfspider.helpers.retailer_id import create_retailer_id

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

            images = product.css(".img-fluid")
            disc["image"] = images[0].attrib["src"]

            disc["spider_name"] = self.name
            disc["in_stock"] = True
            disc["retailer"] = self.allowed_domains[0]

            url = product.css('.__product_url').attrib["href"]
            disc["url"] = url

            brand = product.css(".manufacturers::text").get().strip()
            disc["brand"] = brand

            disc["retailer_id"] = create_retailer_id(brand, url)
            disc["price"] = int(product.css(".price::text").get().strip().replace(",-", ""))
    
            flight_specs = product.css('.product_box_tag > span::text').getall()
            flight_specs = [float(spec.replace(",", ".")) for spec in flight_specs]
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs

            yield disc
