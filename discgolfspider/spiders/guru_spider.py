from ..items import DiscItem

import scrapy

class GuruSpider(scrapy.Spider):
  name = "guru"
  allowed_domains = ["gurudiscgolf.no"]
  start_urls = ["https://gurudiscgolf.no/diskgolf.html"]

  def parse(self, response):
    has_subcategories = len(response.css(".row.subcategories div").getall()) > 0

    if has_subcategories:
      for category in response.css(".row.subcategories div"):
        next_page = category.css("a::attr(href)").get()

        if next_page is not None:
          yield response.follow(next_page, callback=self.parse)

    else:
      for product in response.css(".product-layout"):
        disc_name = product.css(".img-responsive::attr(alt)").get()
        in_stock = product.css(".stock-status::text").get() != "Utsolgt"
        
        disc = DiscItem()
        disc["name"] = disc_name
        disc["site"] = self.name
        disc["in_stock"] = in_stock

        yield disc 
