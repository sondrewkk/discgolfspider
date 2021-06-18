from ..items import DiscItem

import scrapy

class DiscgolfdynastySpider(scrapy.Spider):
  name = "discgolfdynasty"
  allowed_domains = ["discgolfdynasty.no"]
  start_urls = [
    "https://www.discgolfdynasty.no"
  ]

  def parse(self, response):
    brands = response.xpath("/html/body/div[1]/nav/div/ul[2]/li[2]/ul/li")

    for brand in brands:
      brand_path = brand.css("a::attr(href)").get()
      brand_name = brand.css("a::text").get().strip()

      next_page = f"{self.start_urls[0]}{brand_path}"

      if next_page is not None:
        yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand_name})

  def parse_products(self, response, brand):
    for product in response.css(".product-grid-item"):
      disc = DiscItem()
      disc["name"] = product.css("p::text").get().split(" ", 1)[1]     
      disc["image"] = product.css("img::attr(src)").get()
      disc["spider_name"] = self.name
      disc["brand"] = brand
      disc["retailer"] = self.allowed_domains[0]
      disc["price"] = int(product.css("small::text").get())
      disc["speed"] = None
      disc["glide"] = None
      disc["turn"] = None
      disc["fade"] = None
      
      sold_out = product.css(".badge--sold-out").get()
      disc["in_stock"] = True if not sold_out else False

      url = product.css("a::attr(href)").get()
      disc["url"] = f"{self.start_urls[0]}{url}"
      
      yield disc
    
    next_page = response.css(".pagination-custom a[title='Neste »']::attr(href)").get()
  
    if next_page is not None:
      next_page = f"{self.start_urls[0]}{next_page}"
      yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
    