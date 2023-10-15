import scrapy
from urllib.parse import urlparse, parse_qs
from discgolfspider.helpers.retailer_id import create_retailer_id

from discgolfspider.items import CreateDiscItem


class DiscgolfWheelieSpider(scrapy.Spider):
    name = "discgolf_wheelie"
    allowed_domains = ["discgolf-wheelie.no"]
    start_urls = ["https://discgolf-wheelie.no/json/products?currencyIso=NOK&field=categoryId&filter=%7B%7D&filterGenerate=true&id=3&limit=0&orderBy=Sorting,-Sold&page=1"]
    parsed_products = 0

    def parse(self, response):
        products = response.json()["products"]
        products = self.clean_products(products)

        for product in products:
            try:
                disc = CreateDiscItem()
                disc["name"] = product["Title"].title()
                disc["spider_name"] = self.name

                brand = product["ProducerTitle"]
                disc["brand"] = brand
                disc["retailer"] = self.allowed_domains[0]

                url = self.create_product_url(product["Handle"])
                disc["url"] = url
                disc["retailer_id"] = create_retailer_id(brand, url)
                disc["image"] = self.create_image_url(product["Images"][0])

                disc["in_stock"] = True if not product["Soldout"] else False
                disc["price"] = product["Prices"][0]["FullPriceMax"]
                disc["speed"], disc["glide"], disc["turn"], disc["fade"] = self.get_flight_spec(product["DescriptionList"])

                yield disc
            except Exception as e:
                self.logger.error(f"Error parsing disc: {product['title']}({self.create_product_url(product['handle'])}). Reason: {e}")

    def clean_products(self, products: list) -> list:
        return [
            product for product in products 
            if product["Title"].lower().find("start sett") < 0
            and product["CategoryTitle"] != "TILBEHØR"
        ]

    def next_page_url(self, url):
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)

        page = int(query["page"][0])
        next_page_url = parsed_url._replace(query=f"currencyIso=NOK&field=categoryId&filter=%7B%7D&filterGenerate=true&id=3&limit=24&orderBy=Sorting,-Sold&page={page + 1}").geturl()

        return next_page_url

    def create_product_url(self, product_handle: str):
        return f"https://discgolf-wheelie.no{product_handle}"

    def create_image_url(self, image_url: str):
        if not image_url:
            raise ValueError("image_url cannot be None")

        return f"https://shop88398.sfstatic.io{image_url}"

    def get_flight_spec(self, description_list):
        flight_specs = {
            "speed": None,
            "glide": None,
            "turn": None,
            "fade": None
        }

        # description_list is a string with html tags. Create a scrapy selector to parse the html
        selector = scrapy.Selector(text=description_list)

        # get td elements and drop the first 4 elements
        tds = selector.css("td::text").getall()[4:8]

        # try to cast string value to float for each td element and store in flight_specs
        for key, td in zip(flight_specs.keys(), tds):
            try:
                flight_specs[key] = float(td)  # type: ignore 
            except ValueError:
                self.logger.warning(f"Could not cast {td} to float")

        return list(flight_specs.values())
