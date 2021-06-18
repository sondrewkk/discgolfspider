from ..items import DiscItem

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
          yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand_name})
   
   
  def parse_products(self, response, brand):
    has_subcategories = len(response.css(".row.subcategories div").getall()) > 0

    if has_subcategories:
      for category in response.css(".row.subcategories div"):
        next_page = category.css("a::attr(href)").get()
        

        if next_page is not None:
          yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
    else:
      for product in response.css(".product-layout"):
        disc = DiscItem()
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
          disc["price"] = int(''.join(filter(str.isdigit, price.split(",")[0])))

        if len(flight_specs) == 4:
          disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs
        
        yield disc 
