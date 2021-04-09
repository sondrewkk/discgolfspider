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
        
        disc = DiscItem()

        disc["name"] = disc_name
        disc["site"] = self.name

        yield disc
      
    next_page = response.css("li.pages-item-next a::attr(href)").get()

    if next_page is not None:
      yield response.follow(next_page, callback=self.parse)

    
