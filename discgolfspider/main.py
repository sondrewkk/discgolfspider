from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging, logger
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor, task

from discgolfspider.spiders.aceshop_spider import AceshopSpider
from discgolfspider.spiders.chicks_with_discs_spider import ChickWithDiscsSpider
from discgolfspider.spiders.dgshop_spider import DgshopSpider
from discgolfspider.spiders.discgolfdynasty_spider import DiscgolfdynastySpider
from discgolfspider.spiders.discoverdiscs_spider import DiscoverdiscsSpider
from discgolfspider.spiders.discshopen_spider import DiscshopenSpider
from discgolfspider.spiders.discsor_spider import DiscsorSpider
from discgolfspider.spiders.frisbeebutikken_spider import FrisbeebutikkenSpider
from discgolfspider.spiders.frisbeesor_spider import FrisbeesorSpider
from discgolfspider.spiders.golfkongen_spider import GolfkongenSpider
from discgolfspider.spiders.kastmeg_spider import KastmegSpider
from discgolfspider.spiders.prodisc_spider import ProdiscSpider
from discgolfspider.spiders.sendeskive_spider import SendeskiveSpider
from discgolfspider.spiders.wearediscgolf_spider import WeAreDiscgolfSpider
import os

settings = get_project_settings()
log_level = os.getenv("LOG_LEVEL")

runner = None


@defer.inlineCallbacks
def crawl():
    try:
        # yield runner.crawl(WeAreDiscgolfSpider)
        # yield runner.crawl(AceshopSpider)
        # yield runner.crawl(FrisbeebutikkenSpider)
        # yield runner.crawl(FrisbeesorSpider)
        # yield runner.crawl(DiscgolfdynastySpider)
        # yield runner.crawl(DiscoverdiscsSpider)
        # yield runner.crawl(ProdiscSpider)
        # yield runner.crawl(DiscshopenSpider)
        # yield runner.crawl(SendeskiveSpider)
        # yield runner.crawl(GolfkongenSpider)
        # yield runner.crawl(KastmegSpider)
        # yield runner.crawl(DiscsorSpider)
        # yield runner.crawl(DgshopSpider)
        yield runner.crawl(ChickWithDiscsSpider)
    except Exception as e:
        logger.error(f"Error in crawl: {e}")

    return


def cb_loop_done(result):
    logger.info(f"Crawl done. Result: \n {result}")
    reactor.stop()


def cb_loop_error(failure):
    logger.error("Crawl process failed. Reason: \n {}".format(failure))
    reactor.stop()


def start():
    logger.info("Crawl process is starting.")
    print("Crawl process is starting.")

    loop = task.LoopingCall(crawl)
    interval = float(os.getenv("CRAWL_INTERVAL", 3600))

    loopDeferred = loop.start(interval)
    loopDeferred.addCallback(cb_loop_done)
    loopDeferred.addErrback(cb_loop_error)

    reactor.run()  # Blocks until last crawl is finished


if __name__ == "__main__":
    print(f"Log level: {log_level}")

    configure_logging({"LOG_LEVEL": log_level})

    runner = CrawlerRunner(settings)

    logger.info("Starting the spider...")

    start()
