import traceback
from typing import Optional
from scrapy.http import Headers
from scrapy import Request
from discgolfspider.helpers.brand_helper import BrandHelper
from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem

#import discgolfspider.settings as settings
import scrapy


class DiscshopenSpider(scrapy.Spider):
    name = "discshopen"
    allowed_domains = ["discshopen.no"]
    start_urls = ["https://discshopen.no/wp-json/wc/v3/products?page=1"]
    http_auth_domain = "discshopen.no"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        settings = kwargs["settings"]
        self.http_user = settings["DISCSHOPEN_API_KEY"]
        self.http_pass = settings["DISCSHOPEN_API_SECRET"]


    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)


    def parse(self, response):
        products = response.json()

        disc_products = [product for product in products if self.is_disc(product)]

        for disc_product in disc_products:

            try:
                # If the disc product is not published, skip this disc product
                if disc_product["status"] == "draft":
                    continue

                disc = CreateDiscItem()
                disc["name"] = disc_product["name"]

                image = "https://discshopen.no/wp-content/uploads/woocommerce-placeholder-416x416.png"
                if len(disc_product["images"]) > 0:
                    image = disc_product["images"][0]["src"]

                disc["image"] = image

                in_stock = True if disc_product["stock_status"] == "instock" else False
                disc["in_stock"] = in_stock
                
                url = disc_product["permalink"]
                disc["url"] = url
                disc["spider_name"] = self.name
                
                #attributes = disc_product["attributes"]
                brand = self.get_brand_from_tags(disc_product["tags"])
                disc["brand"] = brand
                disc["retailer"] = self.allowed_domains[0]
                disc["retailer_id"] = create_retailer_id(brand, url)        # type: ignore
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [None, None, None, None]

                price: int = -9999
                if disc_product["price"]:
                    price = int(disc_product["price"])
                
                disc["price"] = price

                yield disc
            except Exception as e:
                self.logger.error(f"Error parsing disc: {disc_product['name']}({disc_product['permalink']})")
                self.logger.exception(e)

        # Check for next page
        headers: Headers = response.headers
        next_page = self.get_next_page(headers)

        if next_page is not None:
            yield Request(next_page, callback=self.parse)


    def is_disc(self, product: dict) -> bool:
        product_type: str = product["categories"][0]["slug"]
        disc_products = ["distance-driver", "driver", "fairway-driver", "midrange", "putter"]
        return product_type in disc_products


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

    
    def get_brand_from_tags(self, tags: list) -> Optional[str]:
        for tag in tags:
            name = tag["name"]
            self.logger.debug(f"Checking tag: {name}")

            # if "disc" in name:
            #     name = " ".join(tag["name"].split("disc"))
                
            brand = BrandHelper.normalize(name)
            self.logger.debug(f"Brand: {brand}")
            
            if brand is not None:
                return brand

        return None

    # def get_flight_spec_from_description(self, description: str) -> Optional[list[float]]:
    #     self.logger.debug(f"Description: {description}")

    #     description = description.lower()
    #     specs_exist = False
    #     flight_specs = ["speed", "glide", "turn", "fade"]
        
    #     for spec in flight_specs:
    #         specs_exist = True if spec in description else False

    #     if not specs_exist:
    #         return None

        

