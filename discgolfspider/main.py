from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from discgolfspider.spiders.dgshop_spider import DgshopSpider
from discgolfspider.spiders.guru_spider import GuruSpider

configure_logging()
runner = CrawlerRunner(get_project_settings())

@defer.inlineCallbacks
def crawl():
  yield runner.crawl(DgshopSpider)
  yield runner.crawl(GuruSpider)
  reactor.stop()

def start():  
  crawl()
  reactor.run() # Blocks until last crawl is finished