from ..items import CreateDiscItem

import scrapy
import re

class DgshopSpider(scrapy.Spider):
  name = "dgshop"
  allowed_domains = ["dgshop.no"]
  start_urls = [
    "https://www.dgshop.no/"
  ]

  def parse(self, response):
    for brand in response.xpath("/html/body/div[2]/div[1]/div/div[2]/nav/ul/li[2]/ul/li"):
      brand_name = brand.css("a > span::text").get()
      next_page = brand.css("a::attr(href)").get()

      if next_page is not None:
        yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand_name})
  
  def parse_products(self, response, brand):
    for product in response.css(".product-item-info"):
      disc = CreateDiscItem()
      disc["name"] = product.css(".product-image-photo::attr(alt)").get()
      disc["image"] = product.css(".product-image-photo::attr(src)").get()
      disc["url"] = product.css("a::attr(href)").get()
      disc["spider_name"] = self.name
      disc["in_stock"] = True
      disc["retailer"] = self.allowed_domains[0]
      disc["brand"] = brand
      
      price = product.css(".price::text").get()
      flight_specs = product.css(".flight-rating > text::text").getall()

      if price:
        disc["price"] = int(price.split(",")[0])
        
      if len(flight_specs) == 4:
        flight_specs = [float(numeric_string.replace(",", ".")) for numeric_string in flight_specs]
        disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs
      else:
        self.logger.warning(f"Did not find flight spec for disc with name { disc['name'] }")
        disc["speed"] = None
        disc["glide"] = None
        disc["turn"] = None
        disc["fade"] = None

      yield disc
      
    next_page = response.css("li.pages-item-next a::attr(href)").get()

    if next_page is not None:
      yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
    