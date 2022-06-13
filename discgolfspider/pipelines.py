# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import Spider
from discgolfspider.discinstock_api import DiscinstockApi
from scrapy.exceptions import DropItem
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
            spider.logger.error(
                f"Could not scrape brand name ({ 'None' if not disc['brand'] else disc['brand']}) for disc with name {disc['name']}."
            )
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

        if not existsing_disc_item:
            spider.logger.debug(f"## Create {disc_item}.")
            disc: DiscItem = self.api.add_disc(disc_item)
        else:
            spider.logger.debug(f" ## Update {disc_item}")
            disc: DiscItem = self.update_disc(disc_item, existsing_disc_item)
            self.discs = list(filter(lambda disc: disc["_id"] != existsing_disc_item["_id"], self.discs))

        return disc


    def get_existing_disc_item(self, disc_item: CreateDiscItem) -> DiscItem:
        if not self.discs:
            return None

        existing_disc: DiscItem = next((d for d in self.discs if d["retailer_id"] == disc_item["retailer_id"]), None)
        return existing_disc


    def update_disc(self, disc: CreateDiscItem, current_disc: DiscItem) -> DiscItem:
        
        # Get the difference between the newly scraped disc item and the one stored in db
        disc_difference = self.get_disc_difference(disc, current_disc)
        self.spider.logger.debug(f"## {disc_difference=}")

        # If there is no updates return the crawled disc
        if not disc_difference:
            self.spider.logger.info(f"{disc} has nothing to update.")
            return disc

        # Only update flight spec if the scraped item has value and stored has None
        #remove_flight_spec_items = []
        for diff_k, diff_v in disc_difference.items():
            if self.is_flight_spec(diff_k) and self.is_flight_spec_updateable(diff_v, disc[diff_k]):
                disc_difference.pop(diff_k)
                #remove_flight_spec_items.append(diff_k)

        #for remove_item in remove_flight_spec_items:
        #    disc_difference.pop(remove_item)


        self.spider.logger.debug(f"{disc_difference=}")        

        # Update difference
        updated_disc: DiscItem = self.api.patch_disc(current_disc["_id"], disc_difference)
        return updated_disc


    def get_disc_difference(self, disc: CreateDiscItem, current_disc: DiscItem) -> dict:
        difference = {}

        for k, v in current_disc.items():
            if k in disc.keys():
                equal: bool = disc[k] == v

                if not equal:
                    difference[k] = disc[k]

        return difference


    def is_flight_spec(self, spec_type: str) -> bool:
        return spec_type.lower() in ("speed", "glide", "turn", "fade")
    

    def is_flight_spec_updateable(self, new: float, old: float) -> bool:
        self.spider.logger.debug(f"{new=} | {old=}")
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
            enabled=crawler.settings.get("ENABLE_DISC_ITEM_FLIGHT_SPEC_PIPELINE")
        )

    def process_item(self, item: CreateDiscItem, spider):
        
        if not self.enabled:
            return item

        disc_item: CreateDiscItem = item
            
        # Id disc item already has specs return
        if disc_item["speed"] is not None:
            return disc_item

        # Get discs with same name and has values for flight specs
        query = {"disc_name": disc_item["name"]}
        discs = self.api.search_disc(query)
        discs = [disc for disc in discs if disc["speed"] is not None]

        flight_spec_suggestion: dict

        try:
            flight_spec_suggestion = FlightSpecSuggester.find_suggestion(discs)
        except SuggestionError as err:
            spider.logger.info(f"Could not find suggestion for {disc_item}. Message: {err}")
            return disc_item

        spider.logger.info(f"SUCCESSFULLY found flight spec for {disc_item}")
        disc_item["speed"] = flight_spec_suggestion["speed"]
        disc_item["glide"] = flight_spec_suggestion["glide"]
        disc_item["turn"]  = flight_spec_suggestion["turn"]
        disc_item["fade"]  = flight_spec_suggestion["fade"]

        return disc_item
        