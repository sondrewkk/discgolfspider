from ..items import DiscItem

import scrapy

class GolfdiscerSpider(scrapy.Spider):
  name = "golfdiscer"
  allowed_domains = ["golfdiscer.no"]
  start_urls = [
    "https://golfdiscer.no"
  ]

  def parse(self, response):
    brands = response.css(".top-navigation > li ul.level0").xpath("li[2]/div/ul/li")

    for brand in brands:
      brand_path = brand.css("a::attr(href)").get()
      brand_name = brand.css("a::text").get().rstrip("\n")

      next_page = f"{self.start_urls[0]}{brand_path}"

      if next_page is not None:
        yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand_name})

  def parse_products(self, response, brand):
    for product in response.css(".product-inner"):
      disc = DiscItem()
      disc["name"] = product.css(".product-loop-title > h3::text").get().strip()
      disc["image"] = product.css(".product-image img::attr(data-src)").get()
      disc["in_stock"] = product.css(".add-links-wrap span::text").get() != "Utsolgt"
      disc["spider_name"] = self.name
      disc["brand"] = brand
      disc["retailer"] = self.allowed_domains[0]
      disc["price"] = int(product.css(".money::text").get().split(",")[0])
      disc["speed"] = product.css(".flight-numbers > li span::text").get().strip()
      disc["glide"] = product.css(".flight-numbers > li:nth-child(2)::text").get().strip()
      disc["turn"] = product.css(".flight-numbers > li:nth-child(3)::text").get().strip()
      disc["fade"] = product.css(".flight-numbers > li:nth-child(4)::text").get().strip()

      url = product.css(".product-image > a::attr(href)").get()
      disc["url"] = f"{self.start_urls[0]}{url}"
      
      yield disc
    
    next_page = response.css(".pagination-page a[title=Neste]::attr(href)").get()

    if next_page is not None:
      yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
    