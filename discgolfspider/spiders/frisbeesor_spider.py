import scrapy

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem


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

            if next_page is not None and brand_name != "ZÜCA":
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        products = self.clean_products(response.css(".product"))

        for product in products:
            disc = CreateDiscItem()
            disc["name"] = product.css(".name > a::text").get().lower().title()
            disc["image"] = product.css("img::attr(src)").get()

            is_out_of_stock = product.css(".out-of-stock-label")
            disc["in_stock"] = False if is_out_of_stock else True

            url = product.css("a::attr(href)").get()
            disc["url"] = url
            disc["spider_name"] = self.name
            disc["brand"] = brand
            disc["retailer"] = self.allowed_domains[0]
            disc["retailer_id"] = create_retailer_id(brand, url)
            disc["speed"] = None
            disc["glide"] = None
            disc["turn"] = None
            disc["fade"] = None

            price = product.css(".price bdi::text").get()

            if price:
                disc["price"] = int("".join(filter(str.isdigit, price.replace(",", "").split(".")[0])))
            else:
                disc["price"] = None

            if "pakke" in disc["name"].lower():
                continue

            yield disc

        next_page = response.css("a.next::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})

    def clean_products(self, products: list) -> list:
        """Removes products that has a category that is not valid, represented by non_valid_categories array

        Args:
            products (list): List of products

        Returns:
            list: List of products that has a valid category
        """
        non_valid_categories = [
            "product_cat-kurver",
            "product_cat-tilbehor",
            "product_cat-sekker",
            "product_cat-startersett",
            "product_cat-klaer",
        ]

        return [p for p in products if not [True for c in non_valid_categories if c in p.attrib["class"]]]
