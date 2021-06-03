from twisted.internet import reactor, defer, task
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from .spiders.dgshop_spider import DgshopSpider
from .spiders.guru_spider import GuruSpider
from .spiders.aceshop_spider import AceshopSpider
from .spiders.krokholdgs_spider import KrokholDgsSpider


configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
  # yield runner.crawl(DgshopSpider)
  # yield runner.crawl(GuruSpider)
  # yield runner.crawl(AceshopSpider)
  yield runner.crawl(KrokholDgsSpider)

  return

def cb_loop_done(result):
  print("Crawl loop done")
  reactor.stop()

def cb_loop_error(failure):
  print(failure.getBriefTraceback())
  reactor.stop()

def start():  
  loop = task.LoopingCall(crawl)
  interval = settings["CRAWL_INTERVAL"]

  loopDeferred = loop.start(interval)
  loopDeferred.addCallback(cb_loop_done)
  loopDeferred.addErrback(cb_loop_error)

  reactor.run() # Blocks until last crawl is finished

if __name__ == "__main__":
 start()