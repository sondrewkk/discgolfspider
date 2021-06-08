from ..items import DiscItem
from scrapy.utils.response import open_in_browser
from urllib.parse import parse_qs, urlparse

import scrapy

class FrisbeebutikkenSpider(scrapy.Spider):
  name = "frisbeebutikken"
  allowed_domains = ["frisbeebutikken.no", "app.selz.com"]
  start_urls = [
    "https://app.selz.com/sdk/products/all/181662?q=&c=5ca31978701f5d0dd4dc0b22&p=1", # Discmania
    "https://app.selz.com/sdk/products/all/181662?q=&c=5ca006f9701f5d08f01a44ff&p=1", # Innova
    "https://app.selz.com/sdk/products/all/181662?q=&c=5ca00656701f5d08f01a43fb&p=1", # Latitude64
    "https://app.selz.com/sdk/products/all/181662?q=&c=5cceae5e701f5d0fb89ac9db&p=1", # Discraft
    "https://app.selz.com/sdk/products/all/181662?q=&c=5ca00775701f5d0ce4d92c0d&p=1", # Dynamic discs
    "https://app.selz.com/sdk/products/all/181662?q=&c=5ca00825701f5d0ce4d92ceb&p=1", # Westside discs
  ]

  brand_map = {
    "Discmania": "5ca31978701f5d0dd4dc0b22",
    "Innova": "5ca006f9701f5d08f01a44ff",
    "Latitude 64": "5ca00656701f5d08f01a43",
    "Discraft": "5cceae5e701f5d0fb89ac9db",
    "Dynamic Discs": "5ca00775701f5d0ce4d92c0d",
    "Westside Discs": "5ca00825701f5d0ce4d92ceb",
  }

  def parse(self, response):
    data = response.json()["data"]
    products = data["products"]
    current_page = data["page"]
    pages = data["pages"]
    
    url = urlparse(response.url)
    brand_id = parse_qs(url.query)["c"][0]
    brand_name = self.get_brand(brand_id)

    for product in products:
      disc = DiscItem()
      disc["name"] = product["title"]
      disc["url"] = product["urls"]["full"]
      disc["image"] = product["featured_image"]["original"]
      disc["in_stock"] = product["is_sold_out"] == False
      disc["spider_name"] = self.name 
      disc["brand"] = brand_name
      disc["retailer"] = self.allowed_domains[0]
      disc["price"] = int(product["price"])
      disc["speed"] = None
      disc["glide"] = None
      disc["turn"] = None
      disc["fade"] = None

      yield disc

    if current_page < pages:
      next_page = response.url.replace(f"p={ current_page }", f"p={ current_page + 1 }")
      self.logger.debug(f"next={next_page}")
      yield response.follow(next_page, callback=self.parse)
   

  def get_brand(self, id: str):
    for key, value in self.brand_map.items():
      if id == value:
        return key
    
    return ""
