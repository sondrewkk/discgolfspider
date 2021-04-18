from ..items import DiscItem

import scrapy

class DgshopSpider(scrapy.Spider):
  name = "dgshop"
  allowed_domains = ["dgshop.no"]
  start_urls = [
    "https://www.dgshop.no/discer?product_list_limit=48"
  ]

  def parse(self, response):
    for product in response.css(".product-item-info"):
        disc_name = product.css(".product-image-photo::attr(alt)").get()
        disc_image = product.css(".product-image-photo::attr(src)").get()
        disc_url = product.css("a::attr(href)").get()

        self.log(f"disc_url = {disc_url}")
        
        disc = DiscItem()
        disc["name"] = disc_name
        disc["image"] = disc_image
        disc["spider_name"] = self.name
        disc["in_stock"] = True
        disc["url"] = disc_url
        disc["retailer"] = self.allowed_domains[0]

        yield disc
      
    next_page = response.css("li.pages-item-next a::attr(href)").get()

    if next_page is not None:
      yield response.follow(next_page, callback=self.parse)

    
