import scrapy

from discgolfspider.helpers.retailer_id import create_retailer_id
from discgolfspider.items import CreateDiscItem


class BogeyshopSpider(scrapy.Spider):
    name = "bogeyshop"
    allowed_domains = ["bogeyshop.no"]
    start_urls = ["https://www.bogeyshop.no/discer"]
    base_url = "https://www.bogeyshop.no"

    def parse(self, response):
        brand_links: list[str] = response.css(".b-e-f-i > a::attr(href)").getall()
        brands = brand_links[1:]

        for brand in brands:
            brand_name = brand.split("=")[-1]
            next_page = response.urljoin(brand)

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        products = response.css(".item-wrapper")

        for product in products:
            disc = CreateDiscItem()

            try:
                disc_name: str = product.css(".prd-title-c::text").get()
                disc["name"] = disc_name.replace("\r", "").replace("\n", "").strip()

                handle: str = product.css("a::attr(href)").get()
                url = f"{self.base_url}{handle}"
                disc["url"] = url

                image: str = product.css("img::attr(src)").get()
                disc["image"] = image if image else "https://via.placeholder.com/300"

                disc["spider_name"] = self.name
                disc["retailer"] = self.allowed_domains[0]
                disc["retailer_id"] = create_retailer_id(brand, url)

                # Needs some adjustment for the brand name
                disc["brand"] = brand.replace("-", " ").replace("64", " 64").replace("loft", "løft")

                out_of_stock: str = product.css(".prd-out-of-stock-c::text").get()
                disc["in_stock"] = out_of_stock != "Ikke på lager"

                price: str = product.css(".prd-price-c::text").get()
                if not price:
                    raise ValueError("No price found")

                disc["price"] = int(price.split(",")[0])

                # There is no flight specs available on the site
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = [None, None, None, None]

                yield scrapy.Request(
                    disc["url"],
                    callback=self.parse_disc_details,
                    cb_kwargs={"disc": disc},
                )
            except Exception as e:
                self.logger.error(f"Error parsing disc: {disc}): {e}")

        next_page = response.css("a.pager-next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_products, cb_kwargs={"brand": brand})

    def parse_disc_details(self, response, disc: CreateDiscItem):
        full_name: str = response.css(".prd-text-c > p::text").get()
        disc["name"] = full_name

        yield disc
