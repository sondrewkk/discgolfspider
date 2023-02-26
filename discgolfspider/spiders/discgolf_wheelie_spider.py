import scrapy
from urllib.parse import urlparse, parse_qs
from discgolfspider.helpers.retailer_id import create_retailer_id

from discgolfspider.items import CreateDiscItem

class DiscgolfWheelieSpider(scrapy.Spider):
    name = "discgolf_wheelie"
    allowed_domains = ["discgolf-wheelie.no"]
    start_urls = ["https://discgolf-wheelie.no/json/products?currencyIso=NOK&field=categoryId&filter=%7B%7D&filterGenerate=true&id=3&limit=24&orderBy=Sorting,-Sold&page=1"]
    parsed_products = 0

    def parse(self, response):
        
        amount_of_products = response.json()["amount"]
        products = response.json()["products"]

        for product in products:
            self.parse_product(product)
        
        self.parsed_products += len(products)
        if self.parsed_products < amount_of_products:
            next_page = self.next_page_url(response.url)
            yield scrapy.Request(next_page, callback=self.parse)
        
    def parse_product(self, product):
        self.logger.debug(f"product: {product['Title']}")

        try:
            disc = CreateDiscItem()
            disc["name"] = product["Title"]
            disc["spider_name"] = self.name

            brand = product["ProducerTitle"]
            disc["brand"] = brand
            disc["retailer"] = self.allowed_domains[0]

            url = self.create_product_url(product["Handle"])
            disc["url"] = url
            disc["retailer_id"] = create_retailer_id(brand, url)
            disc["image"] = product["Images"][0]

            #variants = product["variants"]
            disc["in_stock"] = product["Soldout"]
            disc["price"] = product["Prices"][0]["FullPriceMax"]
            disc["speed"], disc["glide"], disc["turn"], disc["fade"] = self.get_flight_spec(product["DescriptionList"])

            yield disc
        except Exception as e:
            self.logger.error(f"Error parsing disc: {product['title']}({self.create_product_url(product['handle'])})")
            self.logger.error(e)


    def next_page_url(self, url):
        # parse url and change limit to the double amout of page. Page is the page + 1
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        page = int(query["page"][0])
        limit = int(query["limit"][0])

        next_page_url = parsed_url._replace(query=f"currencyIso=NOK&field=categoryId&filter=%7B%7D&filterGenerate=true&id=3&limit={limit + (limit / page)}&orderBy=Sorting,-Sold&page={page + 1}").geturl()
        self.logger.debug(f"next_page_url: {next_page_url}")
        return next_page_url

    def create_product_url(self, product_handle: str):
        return f"https:/discgolf-wheelie.no/products/{product_handle}"
    
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
        tds = selector.css("td::text").getall()[4:]

        # try to cast string value to float for each td element
        for td in tds:
            try:
                td = float(td)
            except ValueError:
                self.logger.warning(f"Could not cast {td} to float")



        # <table border="1" cellpadding="1" cellspacing="1" ""class="skjul-ved-mobil-table" style="width: 100%;">\r\n""\t
        # <tbody>\r\n""\t\t<tr>\r\n""\t\t\t
        # <td style="text-align: center; ""background-color:#f1c40f;color:#FFFFFF;font-weight:bold;">SPEED</td>\r\n""\t\t\t
        # <td style="text-align: center; ""background-color:#000000;color:#FFFFFF;font-weight:bold;">GLIDE</td>\r\n""\t\t\t
        # <td style="text-align: center; ""background-color:#f1c40f;color:#FFFFFF;font-weight:bold;">TURN</td>\r\n""\t\t\t
        # <td style="text-align: center; ""background-color:#000000;color:#FFFFFF;font-weight:bold;">FADE</td>\r\n""\t\t
        # </tr>\r\n""\t\t<tr>\r\n""\t\t\t
        # <td style="text-align: center; ""background-color:#f1c40f;color:#FFFFFF;font-weight:bold;">5</td>\r\n""\t\t\t
        # <td style="text-align: center; ""background-color:#000000;color:#FFFFFF;font-weight:bold;">5</td>\r\n""\t\t\t
        # <td style="text-align: center; ""background-color:#f1c40f;color:#FFFFFF;font-weight:bold;">-1</td>\r\n""\t\t\t
        # <td style="text-align: center; ""background-color:#000000;color:#FFFFFF;font-weight:bold;">1</td>\r\n""\t\t</tr>\r\n""\t
        # 
        # </tbody>\r\n""</table>\r\n""\r\n""<table border="1" cellpadding="1" cellspacing="1" ""class="skjul-ved-desktop-table" style="width: 100%;">\r\n""\t<tbody>\r\n""\t\t<tr>\r\n""\t\t\t<td style="text-align: center; ""background-color:#f1c40f;color:#FFFFFF;font-weight:bold;">S</td>\r\n""\t\t\t<td style="text-align: center; ""background-color:#000000;color:#FFFFFF;font-weight:bold;">G</td>\r\n""\t\t\t<td style="text-align: center; ""background-color:#f1c40f;color:#FFFFFF;font-weight:bold;">T</td>\r\n""\t\t\t<td style="text-align: center; ""background-color:#000000;color:#FFFFFF;font-weight:bold;">F</td>\r\n""\t\t</tr>\r\n""\t\t<tr>\r\n""\t\t\t<td style="text-align: center; ""background-color:#f1c40f;color:#FFFFFF;font-weight:bold;">5</td>\r\n""\t\t\t<td style="text-align: center; ""background-color:#000000;color:#FFFFFF;font-weight:bold;">5</td>\r\n""\t\t\t<td style="text-align: center; ""background-color:#f1c40f;color:#FFFFFF;font-weight:bold;">-1</td>\r\n""\t\t\t<td style="text-align: center; ""background-color:#000000;color:#FFFFFF;font-weight:bold;">1</td>\r\n""\t\t</tr>\r\n""\t</tbody>\r\n""</table>\r\n""\r\n""<p>&nbsp;</p>\r\n""\r\n""<p><strong>FARGEN ER P&Aring; RIM!</strong></p>\r\n""\r\n""<p>&nbsp;</p>\r\n",
        
        
        return speed, glide, turn, fade