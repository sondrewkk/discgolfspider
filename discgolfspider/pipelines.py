# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.utils.log import logger
from .helpers.brand_helper import BrandHelper
from .items import DiscItem


class DiscItemPipeline:
    def process_item(self, item, spider):
        disc = DiscItem(item)

        if not disc["name"]:
            raise DropItem("Missing name")

        if not disc["price"]:
            raise DropItem("No price on disc")

        if disc["price"] and disc["price"] >= 500:
            raise DropItem("Probably not a disc. Price is to high")

        return item

class DiscItemBrandPipeline:
    def process_item(self, item, spider):
        disc = DiscItem(item)
        brand_normalized = BrandHelper.normalize(disc["brand"])

        if not brand_normalized:
            raise DropItem("Unkown brand name")

        disc["brand"] = brand_normalized
        
        return disc

class MongoDBPipeline:
    collection_name = "discs"
    new_discs = []

    def __init__(self, mongo_host, mongo_port, mongo_db, mongo_user, mongo_user_password):
        self.mongo_host=mongo_host
        self.mongo_port=mongo_port
        self.mongo_db=mongo_db
        self.mongo_user=mongo_user
        self.mongo_user_password=mongo_user_password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get("MONGO_HOST"),
            mongo_port=crawler.settings.get("MONGO_PORT"),
            mongo_db=crawler.settings.get("MONGO_DB"),
            mongo_user=crawler.settings.get("MONGO_NON_ROOT_USERNAME"),
            mongo_user_password=crawler.settings.get("MONGO_NON_ROOT_PASSWORD")
        )
    
    def open_spider(self, spider):
        logger.info(f"Crawling {spider.name}")

        if self.mongo_user:
            self.client = pymongo.MongoClient(host=self.mongo_host, port=self.mongo_port, username=self.mongo_user, password=self.mongo_user_password, authSource=self.mongo_db)
        else:
            self.client = pymongo.MongoClient(host=self.mongo_host, port=self.mongo_port)

        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        discs = self.db[self.collection_name]
        
        discs.delete_many({"spider_name": spider.name})
        discs.insert_many(self.new_discs)
        self.new_discs.clear()
        
        self.client.close()

    def process_item(self, item, spider):
        disc = ItemAdapter(item).asdict()
        self.new_discs.append(disc)
        
        return item
