# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import Spider
from scrapy.exceptions import DropItem

from discgolfspider.discinstock_api import DiscinstockApi
from discgolfspider.helpers.brand_helper import BrandHelper
from discgolfspider.helpers.flightspec_suggester import FlightSpecSuggester, SuggestionError
from discgolfspider.items import CreateDiscItem, DiscItem


class DiscItemPipeline:
    def process_item(self, item, spider):
        disc = CreateDiscItem(item)

        if not disc["name"]:
            raise DropItem("Missing name")

        if not disc["price"]:
            raise DropItem("No price on disc")

        if disc["price"] and disc["price"] >= 500:
            raise DropItem("Probably not a disc. Price is to high")

        return item


class DiscItemBrandPipeline:
    def process_item(self, item, spider):
        disc = CreateDiscItem(item)

        brand_normalized = BrandHelper.normalize(disc["brand"])

        if not brand_normalized:
            message = f"Could not scrape brand name ({ 'None' if not disc['brand'] else disc['brand']}) for disc with name {disc['name']}. In stock = {disc['in_stock']}"

            if disc["in_stock"]:
                spider.logger.error(message)
            else:
                spider.logger.warning(message)

            raise DropItem("Brand not normalized.")

        disc["brand"] = brand_normalized

        return disc


class UpdateDiscPipeline:
    def __init__(self, api_url, username, password) -> None:
        self.discs = []
        self.api: DiscinstockApi = DiscinstockApi(api_url, username, password)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            api_url=crawler.settings.get("API_URL"),
            username=crawler.settings.get("API_USERNAME"),
            password=crawler.settings.get("API_PASSWORD"),
        )

    def open_spider(self, spider):
        self.spider: Spider = spider

        current_discs = self.api.fetch_discs(spider.name)
        if current_discs:
            self.discs = current_discs

    def close_spider(self, spider):
        # Remaining discs is not in stock any more
        for disc in self.discs:
            id = disc["_id"]
            updated = self.api.patch_disc(id, {"in_stock": False})

            if not updated:
                spider.logger.error("Could not change instock for {id}")

        # Clear all discs for next scraping
        self.discs.clear()

    def process_item(self, item: CreateDiscItem, spider: Spider):
        spider.logger.debug(f"## Processing {item}")
        disc_item: CreateDiscItem = item
        existsing_disc_item = self.get_existing_disc_item(disc_item)
        disc: DiscItem = existsing_disc_item

        if not existsing_disc_item:
            spider.logger.debug(f"## Create {disc_item}.")
            disc = self.api.add_disc(disc_item)
        else:
            spider.logger.debug(f"## Update {disc_item}")
            diff = self.get_disc_difference(disc_item, existsing_disc_item)

            if diff:
                disc = self.update_disc(existsing_disc_item["_id"], diff)

            # Disc shall not be set to not instock in close spider method.
            self.discs = list(filter(lambda disc: disc["_id"] != existsing_disc_item["_id"], self.discs))

        return disc

    def get_existing_disc_item(self, disc_item: CreateDiscItem) -> DiscItem:
        if not self.discs:
            return None

        existing_disc: DiscItem = next((d for d in self.discs if d["retailer_id"] == disc_item["retailer_id"]), None)
        return existing_disc

    def update_disc(self, id: str, diff: dict) -> DiscItem:
        updated_disc: DiscItem = self.api.patch_disc(id, diff)
        return updated_disc

    def get_disc_difference(self, disc: CreateDiscItem, current_disc: DiscItem) -> dict:
        difference = {}
        remove_flight_spec = False

        for k, v in current_disc.items():
            if k in disc.keys():
                equal: bool = disc[k] == v

                if not equal:
                    difference[k] = disc[k]

        self.spider.logger.debug(f"## {difference=}")

        # If there is no updates return the crawled disc
        if not difference:
            self.spider.logger.debug(f"{disc} has nothing to update.")
            return difference

        # Only update flight spec if the scraped item has value and stored has None
        # If the stored item already has a value, skip update. The stored disc
        # is weighted more than a new disc.
        for k in difference.keys():
            if (
                self.is_flight_spec(k)
                and not self.is_flight_spec_updateable(disc[k], current_disc[k])
                and not remove_flight_spec
            ):
                self.spider.logger.debug(
                    f"Crawled disc has different {k} value than the stored disc. {disc[k]} | {current_disc[k]}. Flag flightspec for removal."
                )
                remove_flight_spec = True

        if remove_flight_spec:
            difference = {k: v for (k, v) in difference.items() if not self.is_flight_spec(k)}

        self.spider.logger.debug(f"## {difference=}")

        return difference

    def is_flight_spec(self, spec_type: str) -> bool:
        return spec_type.lower() in ("speed", "glide", "turn", "fade")

    def is_flight_spec_updateable(self, new: float, old: float) -> bool:
        return new is not None and old is None


class DiscItemFlightSpecPipeline:
    def __init__(self, api_url: str, username: str, password: str, enabled: bool) -> None:
        self.api: DiscinstockApi = DiscinstockApi(api_url, username, password)
        self.enabled = enabled

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            api_url=crawler.settings.get("API_URL"),
            username=crawler.settings.get("API_USERNAME"),
            password=crawler.settings.get("API_PASSWORD"),
            enabled=crawler.settings.get("ENABLE_DISC_ITEM_FLIGHT_SPEC_PIPELINE"),
        )

    def process_item(self, item: CreateDiscItem, spider: Spider):
        self.spider = spider

        if not self.enabled:
            spider.logger.debug("Flight spec pipeline is not enabled.")
            return item

        disc_item: CreateDiscItem = item

        # If disc item already has specs return
        if disc_item.has_flight_specs():
            return disc_item

        spider.logger.debug(f"Look for flight spec for {disc_item}")

        # Get discs with same name and has values for flight specs
        query = {"disc_name": disc_item["name"]}
        discs = self.api.search_disc(query)

        spider.logger.debug(f"Before filter: {discs=}")

        discs = list(filter(self.check_disc, discs))
        spider.logger.debug(f" ## Discs with same name: {len(discs)}")

        flight_spec_suggestion = {}

        try:
            flight_spec_suggestion = FlightSpecSuggester.find_suggestion(discs)
        except SuggestionError as err:
            spider.logger.debug(f"Could not find suggestion for {disc_item}. Message: {err}")
            return disc_item

        spider.logger.debug(f"SUCCESSFULLY found flight spec for {disc_item}")
        disc_item["speed"] = flight_spec_suggestion["speed"]
        disc_item["glide"] = flight_spec_suggestion["glide"]
        disc_item["turn"] = flight_spec_suggestion["turn"]
        disc_item["fade"] = flight_spec_suggestion["fade"]

        return disc_item

    def check_disc(self, disc: DiscItem) -> bool:
        has_flight_spec = disc.has_flight_specs()
        self.spider.logger.debug(f"{has_flight_spec=}")
        return has_flight_spec
