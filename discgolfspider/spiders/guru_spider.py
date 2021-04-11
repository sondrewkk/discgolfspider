from ..items import DiscItem

import scrapy

class GuruSpider(scrapy.Spider):
  name = "guru"
  allowed_domains = ["gurudiscgolf.no"]
  # start_urls = [
  #   "https://gurudiscgolf.no/diskgolf/disctroyer.html",
  #   "https://gurudiscgolf.no/diskgolf/infinite-discs/d-blend.html",
  #   "https://gurudiscgolf.no/diskgolf/infinite-discs/g-blend.html",
  #   "https://gurudiscgolf.no/diskgolf/infinite-discs/i-blend.html",
  #   "https://gurudiscgolf.no/diskgolf/infinite-discs/p-blend.html",
  #   "https://gurudiscgolf.no/diskgolf/infinite-discs/x-blend.html",
  #   "https://gurudiscgolf.no/diskgolf/infinite-discs/c-blend.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/innova-special-stamps.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/dx.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/xt.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/pro.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/r-pro.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/champion.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/blizzard-champion.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/halo-star.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/star.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/g-star.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/starlite.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/overmold.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/glow.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/echo-star.html",
  #   "https://gurudiscgolf.no/diskgolf/innova/i-dye.html",
  #   "https://gurudiscgolf.no/diskgolf/sune-sport.html",
  #   "https://gurudiscgolf.no/diskgolf/latitude-64/zero-burst.html",
  #   "https://gurudiscgolf.no/diskgolf/latitude-64/retro.html",
  #   "https://gurudiscgolf.no/diskgolf/latitude-64/zero-line.html",
  #   "https://gurudiscgolf.no/diskgolf/latitude-64/opto-line.html",
  #   "https://gurudiscgolf.no/diskgolf/latitude-64/opto-air.html",
  #   "https://gurudiscgolf.no/diskgolf/latitude-64/opto-x.html",
  #   "https://gurudiscgolf.no/diskgolf/latitude-64/gold-line.html",
  #   "https://gurudiscgolf.no/diskgolf/latitude-64/k2-opto-g.html",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  #   "",
  # ]
  start_urls = ["https://gurudiscgolf.no/diskgolf.html"]

  def parse(self, response):
    subcategories = response.css(".row.subcategories div").getall()

    if len(subcategories) > 0:
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
