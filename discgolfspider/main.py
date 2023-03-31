from twisted.internet import reactor, defer, task
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import logger, configure_logging
from scrapy.crawler import CrawlerRunner
from discgolfspider.crawl_scheduler import CrawlScheduler

from discgolfspider.spiders.guru_spider import GuruSpider
#from discgolfspider.spiders.dgshop_spider import DgshopSpider
from discgolfspider.spiders.aceshop_spider import AceshopSpider
from discgolfspider.spiders.golfdiscer_spider import GolfdiscerSpider
from discgolfspider.spiders.frisbeebutikken_spider import FrisbeebutikkenSpider
#from discgolfspider.spiders.krokholdgs_spider import KrokholDgsSpider
from discgolfspider.spiders.frisbeesor_spider import FrisbeesorSpider
from discgolfspider.spiders.discgolfdynasty_spider import DiscgolfdynastySpider
#from discgolfspider.spiders.frisbeefeber_spider import FrisbeefeberSpider
#from discgolfspider.spiders.spinnvilldg_spider import SpinnvilldgSpider
from discgolfspider.spiders.discoverdiscs_spider import DiscoverdiscsSpider
from discgolfspider.spiders.prodisc_spider import ProdiscSpider
#from discgolfspider.spiders.tbksport_spider import TbksportSpider
from discgolfspider.spiders.starframe_spider import StarframeSpider
from discgolfspider.spiders.discshopen_spider import DiscshopenSpider
from discgolfspider.spiders.discsjappa_spider import DiscsjappaSpider
from discgolfspider.spiders.sendeskive_spider import SendeskiveSpider
from discgolfspider.spiders.discgolf_wheelie_spider import DiscgolfWheelieSpider


def main():  
    scheduler = CrawlScheduler()
    scheduler.run_crawler()


if __name__ == "__main__":
    main()

# @defer.inlineCallbacks
# def crawl():
#     try:
#         #yield runner.crawl(DgshopSpider)               Ingen avtale
#         yield runner.crawl(GuruSpider)                 
#         yield runner.crawl(AceshopSpider)              
#         yield runner.crawl(GolfdiscerSpider)
#         yield runner.crawl(FrisbeebutikkenSpider)
#         #yield runner.crawl(KrokholDgsSpider)           Ingen avtale
#         yield runner.crawl(FrisbeesorSpider)
#         yield runner.crawl(DiscgolfdynastySpider)      
#         #yield runner.crawl(FrisbeefeberSpider)         Ingen avtale
#         #yield runner.crawl(SpinnvilldgSpider)          Ingen avtale
#         yield runner.crawl(DiscoverdiscsSpider)
#         yield runner.crawl(ProdiscSpider)
#         #yield runner.crawl(TbksportSpider)             Ingen avtale
#         yield runner.crawl(StarframeSpider)
#         yield runner.crawl(DiscshopenSpider)
#         yield runner.crawl(DiscsjappaSpider)
#         yield runner.crawl(SendeskiveSpider)
#         yield runner.crawl(DiscgolfWheelieSpider)
#     except Exception as e:
#         logger.error(f"Error in crawl: {e}")

#     return


# def cb_loop_done(result):
#     logger.info(f"Crawl done. Result: \n {result}")
#     reactor.stop()


# def cb_loop_error(failure):
#     logger.error("Crawl process failed. Reason: \n {}".format(failure))
#     reactor.stop()


# def start():
#     logger.info(f"Crawl process is starting.")

#     loop = task.LoopingCall(crawl)
#     interval = settings["CRAWL_INTERVAL"]

#     loopDeferred = loop.start(interval)
#     loopDeferred.addCallback(cb_loop_done)
#     loopDeferred.addErrback(cb_loop_error)

#     reactor.run()  # Blocks until last crawl is finished

# if __name__ == "__main__":
#     start()
