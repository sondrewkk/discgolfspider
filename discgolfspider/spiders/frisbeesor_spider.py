from ..items import CreateDiscItem

import scrapy

class FrisbeesorSpider(scrapy.Spider):
  name = "frisbeesor"
  allowed_domains = ["frisbeesor.no"]
  start_urls = [
    "https://www.frisbeesor.no/produktkategori/merker/"
  ]

  def parse(self, response):
    brands = response.css(".cat-item-133 > ul li")[1:]

    for brand in brands:
      brand_path = brand.css("a::attr(href)").get()
      brand_name = brand.css("a::text").get()

      next_page = f"{brand_path}"

      if next_page is not None:
        yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand_name})

  def parse_products(self, response, brand):
    for product in response.css(".product_item"):
      disc = CreateDiscItem()
      disc["name"] = product.css(".product_archive_title::text").get().lower().title()
      disc["image"] = product.css(".kt-product-animation-contain img::attr(src)").get()
      disc["in_stock"] = product.css(".kad-out-of-stock::text").get() != "utsolgt"
      disc["url"] = product.css(".product_item_link::attr(href)").get()
      disc["spider_name"] = self.name
      disc["brand"] = brand
      disc["retailer"] = self.allowed_domains[0]
      disc["speed"] = None
      disc["glide"] = None
      disc["turn"] = None
      disc["fade"] = None

      price = product.css(".amount > bdi::text").get()
      
      if price:
        disc["price"] = int(price.strip().split(".")[0].replace(",", ""))
      else:
        disc["price"] = None

      yield disc
    
    next_page = response.css("a.next::attr(href)").get()

    if next_page is not None:
      yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
    