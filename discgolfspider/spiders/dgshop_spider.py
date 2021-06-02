from ..items import DiscItem

import scrapy

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
      disc = DiscItem()
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
        disc["price"] = ''.join(filter(str.isdigit, price))
        
      if len(flight_specs) == 4:
        disc["speed"], disc["glide"], disc["turn"], disc["fade"] = flight_specs

      yield disc
      
    next_page = response.css("li.pages-item-next a::attr(href)").get()

    if next_page is not None:
      yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
    