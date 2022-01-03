from ..items import CreateDiscItem

import scrapy


class FrisbeesorSpider(scrapy.Spider):
    name = "frisbeesor"
    allowed_domains = ["frisbeesor.no"]
    start_urls = ["https://www.frisbeesor.no/produktkategori/merker/"]

    def parse(self, response):
        brands = response.css(".product-category")

        for brand in brands:
            brand_path = brand.css("a::attr(href)").get()
            brand_name = brand.css("h5::text").get().strip()

            next_page = f"{brand_path}"

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        
        non_valid_categories = ["product_cat-kurver", "product_cat-tilbehor", "product_cat-sekker"]
        products = response.css(".product")

        # Remove products that has a category tha is not valid, represented by non_valid_categories array
        products = [p for p in products if not [True for c in non_valid_categories if c in p.attrib['class']]]

        for product in products:
            disc = CreateDiscItem()
            disc["name"] = product.css(".name > a::text").get().lower().title()
            disc["image"] = product.css('img::attr(src)').get()
            disc["in_stock"] = True
            disc["url"] = product.css('a::attr(href)').get()
            disc["spider_name"] = self.name
            disc["brand"] = brand
            disc["retailer"] = self.allowed_domains[0]
            disc["speed"] = None
            disc["glide"] = None
            disc["turn"] = None
            disc["fade"] = None

            price = product.css('.price bdi::text').get()

            if price:
                disc["price"] = int(price.split(".")[0])
            else:
                disc["price"] = None

            yield disc

        next_page = response.css('a.next::attr(href)').get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})
