from twisted.internet import reactor, defer, task
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import logger, configure_logging
from scrapy.crawler import CrawlerRunner

from discgolfspider.spiders.wearediscgolf_spider import WeAreDiscgolfSpider
from discgolfspider.spiders.aceshop_spider import AceshopSpider
from discgolfspider.spiders.golfdiscer_spider import GolfdiscerSpider
from discgolfspider.spiders.frisbeebutikken_spider import FrisbeebutikkenSpider
from discgolfspider.spiders.frisbeesor_spider import FrisbeesorSpider
from discgolfspider.spiders.discgolfdynasty_spider import DiscgolfdynastySpider
from discgolfspider.spiders.discoverdiscs_spider import DiscoverdiscsSpider
from discgolfspider.spiders.prodisc_spider import ProdiscSpider
from discgolfspider.spiders.discshopen_spider import DiscshopenSpider
from discgolfspider.spiders.discsjappa_spider import DiscsjappaSpider
from discgolfspider.spiders.sendeskive_spider import SendeskiveSpider
from discgolfspider.spiders.discgolf_wheelie_spider import DiscgolfWheelieSpider


settings = get_project_settings()
configure_logging({"LOG_LEVEL": settings.get("LOG_LEVEL")})

runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl():
    try:
        yield runner.crawl(WeAreDiscgolfSpider)                 
        yield runner.crawl(AceshopSpider)              
        yield runner.crawl(GolfdiscerSpider)
        yield runner.crawl(FrisbeebutikkenSpider)
        yield runner.crawl(FrisbeesorSpider)
        yield runner.crawl(DiscgolfdynastySpider)      
        yield runner.crawl(DiscoverdiscsSpider)
        yield runner.crawl(ProdiscSpider)
        yield runner.crawl(DiscshopenSpider)
        yield runner.crawl(DiscsjappaSpider)
        yield runner.crawl(SendeskiveSpider)
        yield runner.crawl(DiscgolfWheelieSpider)
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
    logger.info(f"Crawl process is starting.")

    loop = task.LoopingCall(crawl)
    interval = settings["CRAWL_INTERVAL"]

    loopDeferred = loop.start(interval)
    loopDeferred.addCallback(cb_loop_done)
    loopDeferred.addErrback(cb_loop_error)

    reactor.run()  # Blocks until last crawl is finished

if __name__ == "__main__":
    start()
