# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from discgolfspider.discinstock_api import DiscinstockApi
from scrapy.exceptions import DropItem
from discgolfspider.helpers.brand_helper import BrandHelper
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
            spider.logger.warning(
                f"Could not scrape brand name ({ 'None' if not disc['brand'] else disc['brand']}) for disc with name {disc['name']}."
            )

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
        self.spider = spider

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

    def process_item(self, item: CreateDiscItem, spider):
        disc_item: CreateDiscItem = item
        existsing_disc_item = self.get_existing_disc_item(disc_item)

        if not existsing_disc_item:
            disc: DiscItem = self.api.add_disc(disc_item)
        else:
            disc: DiscItem = self.update_disc(disc_item, existsing_disc_item)
            self.discs = list(filter(lambda disc: disc["_id"] != existsing_disc_item["_id"], self.discs))

        return disc

    def get_existing_disc_item(self, disc_item: CreateDiscItem) -> DiscItem:
        if not self.discs:
            return None

        existing_disc: DiscItem = next((d for d in self.discs if d["name"] == disc_item["name"]), None)
        return existing_disc

    def update_disc(self, disc: CreateDiscItem, current_disc: DiscItem) -> DiscItem:
        disc_difference = self.get_disc_difference(disc, current_disc)
        id = current_disc["_id"]

        if not disc_difference:
            self.spider.logger.info(f"Disc {id} has nothing to update.")
            return disc

        updated_disc: DiscItem = self.api.patch_disc(id, disc_difference)
        return updated_disc

    def get_disc_difference(self, disc: CreateDiscItem, current_disc: DiscItem) -> dict:
        difference = {}

        for k, v in current_disc.items():
            if k in disc:
                equal: bool = disc[k] == v

                if not equal:
                    difference[k] = disc[k]

        return difference
