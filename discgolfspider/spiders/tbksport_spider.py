from ..items import CreateDiscItem

import scrapy

from urllib.parse import urlparse
from ..helpers.retailer_id import create_retailer_id

class TbksportSpider(scrapy.Spider):
    name = "tbksport"
    allowed_domains = ["tbksport.no"]
    start_urls = ["https://www.tbksport.no/discer/"]

    def parse(self, response):
        brands = response.css("div.bapf_body > ul > li")
        brands = brands[1:]

        for brand in brands:
            brand_name = brand.css("label::text").get()
            product_cat = brand.css("input").attrib["value"]
            next_page = self.create_next_page(product_cat)

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        products = response.css("li.product")
        
        for product in products:
            disc = CreateDiscItem()
            disc["image"] = product.css("img").attrib["src"]
            disc["spider_name"] = self.name
            disc["in_stock"] = True      
           
            url = product.css("a.woocommerce-LoopProduct-link").attrib["href"]        
            disc["url"] = url                                 
            disc["retailer"] = self.allowed_domains[0]
            disc["retailer_id"] = create_retailer_id(brand, url)
            disc["brand"] = brand  
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [None, None, None, None]

            name = product.css("h2::text").get()
            disc["name"] = self.clean_disc_name(name)

            prices = product.css("span.amount > bdi::text").getall()
            prices = [int(price.split(".")[0]) for price in prices]
            price = prices[0]

            if len(prices) > 1:
                price = prices[1]

            disc["price"] = price

            yield disc


        # tbksport does not have enough discs to have multiple pages
        # next_page = response.css("a.pagination__item--prev::attr(href)").get()
        # if next_page is not None:
        #      yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})

    def create_next_page(self, product_cat: int) -> str:
        url = f"{self.start_urls[0]}?filters=product_cat[{product_cat}]"
        
        return urlparse(url).geturl()

    def clean_disc_name(self, name: str) -> str:
        filter_words = ["disc", "discs", "alfa", "innova", "discmania", "discraft", "westside", "kastaplast", "latitude", "prodigy", "viking"]

        # Filter away brands from disc name
        name = name.lower()
        name_splitted = name.split(" ")
        filterd = [word.title() for word in name_splitted if word not in filter_words]
        name_cleaned = " ".join(filterd).split("(")[0].rstrip()

        # Make comments in name lowercase
        #open_parentheses_idx = name_cleaned.find("(")
        #close_parentheses_idx = name_cleaned.find(")")

        #if open_parentheses_idx != -1 and close_parentheses_idx != -1:
        #    comment = name_cleaned[open_parentheses_idx + 1:close_parentheses_idx].lower()
        #    name_cleaned = name_cleaned[:open_parentheses_idx] + "(" + comment + ")" + name_cleaned[close_parentheses_idx + 1:]

        return name_cleaned
