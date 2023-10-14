from discgolfspider.items import CreateDiscItem
from discgolfspider.helpers.retailer_id import create_retailer_id

import scrapy


class DiscgolfdynastySpider(scrapy.Spider):
    name = "discgolfdynasty"
    allowed_domains = ["discgolfdynasty.no"]
    start_urls = ["https://www.discgolfdynasty.no"]

    def parse(self, response):
        brand_links_selector = response.xpath("/html/body/div[2]/header/div/nav/ul/li[2]/details/ul")
        links_href = brand_links_selector.css("a.main-nav__tier-2-link::attr('href')").getall()
        links_data_href = brand_links_selector.css("summary.main-nav__tier-2-link::attr('data-href')").getall()
        brand_links = links_href + links_data_href

        for link in brand_links:
            brand_name = link.split("/")[-1]
            next_page = f"{self.start_urls[0]}{link}"

            if next_page is not None:
                yield response.follow(
                    next_page,
                    callback=self.parse_products,
                    cb_kwargs={"brand": brand_name},
                )

    def parse_products(self, response, brand):
        products = response.css(".product-thumbnail")

        if len(products) == 0:
            self.logger.debug(f"No products found for brand {brand}")
            return

        for product in products:
            disc = CreateDiscItem()
            try:
                brand = brand.replace("-", " ")
                disc["brand"] = brand

                name = product.css(".product-thumbnail__title::text").get()
                disc["name"] = self.format_disc_name(name, brand)

                url = product.css("a").attrib["href"]
                url = f"{self.start_urls[0]}{url}"
                disc["url"] = url

                disc["retailer"] = self.allowed_domains[0]
                disc["retailer_id"] = create_retailer_id(brand, url)
                disc["spider_name"] = self.name

                image = product.css("img::attr(\"src\")").get()
                disc["image"] = image if image else "https://via.placeholder.com/300"

                sold_out = product.css(".product-thumbnail__sold-out-text::text").get()
                disc["in_stock"] = sold_out != "Utsolgt"

                price_text = product.css(".money::text").get()
                price = int(price_text.replace("\n", "").strip().split(",")[0]) if not sold_out else -1
                disc["price"] = price

                yield response.follow(
                    url,
                    callback=self.parse_disc_details,
                    cb_kwargs={"disc": disc},
                )
            except Exception as e:
                self.logger.error(f"Error parsing disc: {disc}): {e}")

        # Check if there is a next page and fowllow it if there is one
        next_page = response.css("a.pagination__next-button::attr(\"href\")").get()

        if next_page is not None:
            yield response.follow(
                next_page,
                callback=self.parse_products,
                cb_kwargs={"brand": brand}
            )

    def format_disc_name(self, name: str, brand: str) -> str:
        formatted = name.replace("\n", "").strip().replace(brand + " ", "")
        formatted = self.remove_brand_from_name(formatted, brand)

        return formatted

    def remove_brand_from_name(self, name: str, brand: str) -> str:
        exclude = set(['discs'])

        # Add brand words to the exclude list if they aren't 'discs'.
        exclude.update(word for word in brand.lower().split(" ") if word != 'discs')

        name_parts = name.split(" ")
        result_parts = [word for word in name_parts if word.lower() not in exclude]

        return ' '.join(result_parts)

    def parse_disc_details(self, response, disc: CreateDiscItem):
        try:
            flight_specs = {"speed": None, "glide": None, "turn": None, "fade": None}
            product_description = response.css(".product__description")
            product_description_values = product_description.css("li::text").getall()

            if product_description_values:
                for description in product_description_values:
                    if ": " in description:
                        key, value = description.split(": ", 1)
                        key = key.lower()
                        if key in flight_specs.keys():
                            flight_specs[key] = float(value.split(" ")[0])

                missing_spec = any(value is None for value in flight_specs.values())
                if missing_spec:
                    self.logger.warning(f"Could not find flight numbers for {disc}: {flight_specs}")
                else:
                    disc["speed"] = flight_specs["speed"]
                    disc["glide"] = flight_specs["glide"]
                    disc["turn"] = flight_specs["turn"]
                    disc["fade"] = flight_specs["fade"]

            yield disc
        except Exception as e:
            self.logger.error(f"Error parsing flight numbers for {disc}): {e}")
