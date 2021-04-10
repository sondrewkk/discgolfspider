# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import logging

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.exceptions import DropItem
from .items import DiscItem


class DiscItemPipeline:
    def process_item(self, item, spider):
        disc = ItemAdapter(item)

        if not disc.get("name"):
            raise DropItem(f"Missing name in {disc}")

        return item


class MongoDBPipeline:
    
    collection_name = "discs"
    current_discs = []
    new_discs = []

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri=mongo_uri
        self.mongo_db=mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DB")
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        discs = self.db[self.collection_name]
        self.current_discs = discs.find({})
        
        discs.delete_many({})
        discs.insert_many(self.new_discs)
        
        self.client.close()

    def process_item(self, item, spider):
        disc = ItemAdapter(item).asdict()
        #self.db[self.collection_name].replace_one(disc, disc, True)
        self.new_discs.append(disc)
        return item
