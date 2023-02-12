from ..items import CreateDiscItem
from ..helpers.retailer_id import create_retailer_id

import scrapy


class DiscoverdiscsSpider(scrapy.Spider):
    name = "discoverdiscs"
    allowed_domains = ["discoverdiscs.no"]
    start_urls = ["https://discoverdiscs.no"]

    def parse(self, response):
        brands = response.css("div[id=\"childlink-Merker\"] > ul > li")

        for brand in brands:
            brand_name = brand.css("a::text").get().strip()
            next_page = brand.css("a::attr(href)").get()

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        
        try:
            products = response.css("li.grid__item")
        
            for product in products:
                disc = CreateDiscItem()
                name = product.css("span.card-information__text::text").get().replace("\n", "").strip()
                url = product.css("a").attrib["href"]
                url = f"{self.start_urls[0]}{url}"
                disc["url"] = url
                disc["retailer_id"] = create_retailer_id(brand, url)

                if self.is_backpack(name, url):
                    self.logger.info(f"Skipping backpack: {name}")
                    continue

                disc["name"] = name
                disc["image"] = product.css("img").attrib["src"]
                disc["spider_name"] = self.name
                
                badge_text = product.css(".badge::text").get()
                disc["in_stock"] = True if badge_text != "Utsolgt" else False
                disc["retailer"] = self.allowed_domains[0]
                disc["brand"] = brand  

                prices = product.css(".price-item::text").getall()
                disc["price"] = int(prices[len(prices) - 1].split(",")[0])

                flight_specs = product.css(".disc-info__value::text").getall()

                if flight_specs and len(flight_specs) == 4:
                    disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [float(spec) for spec in flight_specs]
                else:
                    self.logger.warning(f"{disc['name']}({disc['url']}) is missing flight spec data. {flight_specs=} ")
                    disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [None, None, None, None]

                yield disc
        except Exception as e:
            self.logger.error(f"Error parsing disc: {disc['name']}({disc['url']})")
            self.logger.error(e)

        next_page = response.css("a.pagination__item--prev::attr(href)").get()
        if next_page is not None:
             yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})

    def is_backpack(self, name, url):
        url_contains = "bag" in url or "backpack" in url
        name_contains = "bag" in name.lower() or "backpack" in name.lower()

        return url_contains or name_contains