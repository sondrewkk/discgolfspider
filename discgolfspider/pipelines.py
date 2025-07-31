# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from typing import Optional
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
        brand = disc["brand"]

        if not brand:
            raise DropItem("Missing brand")

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

    def close_spider(self, spider: Spider):
        # Remaining discs is not in stock any more

        spider.logger.info(f"Closing spider {spider.name}. Remaining discs: {len(self.discs)}")
        for disc in self.discs:
            spider.logger.info(f"## {disc['_id']} | {disc['name']} | {disc['in_stock']}")
            if not disc["in_stock"]:
                continue

            id = disc["_id"]
            updated = self.api.patch_disc(id, {"in_stock": False})

            if not updated:
                spider.logger.error("Could not change instock for {id}")

        # Clear all discs for next scraping
        self.discs.clear()

    def process_item(self, item: CreateDiscItem, spider: Spider) -> DiscItem:
        spider.logger.debug(f"## Processing {item}")
        
        disc: DiscItem | None = None
        disc_item: CreateDiscItem = item
        existsing_disc_item = self.get_existing_disc_item(disc_item)

        if not existsing_disc_item:
            spider.logger.debug(f"## Create {disc_item}.")
            disc = self.api.add_disc(disc_item)
        else:
            spider.logger.debug(f"## Update {disc_item}")
            diff = self.get_disc_difference(disc_item, existsing_disc_item)

            if diff:
                disc = self.update_disc(existsing_disc_item["_id"], diff)
            else:
                spider.logger.debug(f"## No updates for {disc_item}.")
                disc = existsing_disc_item
            
            # Disc shall not be set to not instock in close spider method.
            self.discs = [disc for disc in self.discs if disc["_id"] != existsing_disc_item["_id"]]

        if not disc:
            spider.logger.error(f"Could not add or update {disc_item}.")
            raise DropItem(f"Could not add or update {disc_item}")
        
        return disc
    
    def get_existing_disc_item(self, disc_item: CreateDiscItem) -> Optional[DiscItem]:
        if not self.discs:
            return None

        existing_disc: Optional[DiscItem] = next((d for d in self.discs if d["retailer_id"] == disc_item["retailer_id"]), None)
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

        # If there is no updates return the crawled disc
        if not difference:
            self.spider.logger.debug(f"## {disc} has nothing to update.")
            return difference

        self.spider.logger.debug(f"## {current_disc.get('name')}: {difference=}")

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
        disc_item: CreateDiscItem = item

        # If disc item already has specs return
        if disc_item.has_flight_specs():
            return disc_item

        if not self.enabled:
            spider.logger.debug("Flight spec pipeline is not enabled.")
            return item

        search_for_disc_name = disc_item["name"].split(",")[0]
        spider.logger.info(f"Looking for flight spec for {search_for_disc_name}")

        # Get discs with same name and has values for flight specs
        query = {"disc_name": search_for_disc_name}
        discs = self.api.search_disc(query)

        # Filter out discs without flight spec
        discs = [d for d in discs if d.has_flight_spec()]

        if discs:
            try:
                flight_spec_suggestion = FlightSpecSuggester.find_suggestion(discs)
                disc_item.update(flight_spec_suggestion)
                spider.logger.info(f"SUCCESSFULLY found flight spec for {disc_item}")
            except SuggestionError as err:
                spider.logger.warning(f"Could not find flight spec for {disc_item}. Reason: {err}")

        if not disc_item.has_flight_specs():
            spider.logger.warning(
                f"Missing flight spec for {disc_item}. {disc_item.get('speed')=}, {disc_item.get('glide')=}, {disc_item.get('turn')=}, {disc_item.get('fade')=}"
            )

        return disc_item
