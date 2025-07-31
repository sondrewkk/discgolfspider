import os
from scrapy.utils.reactor import install_reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging, logger
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, task

from discgolfspider.spiders.aceshop_spider import AceshopSpider
from discgolfspider.spiders.chicks_with_discs_spider import ChickWithDiscsSpider
from discgolfspider.spiders.dgshop_spider import DgshopSpider
from discgolfspider.spiders.discgolfdynasty_spider import DiscgolfdynastySpider
from discgolfspider.spiders.discshopen_spider import DiscshopenSpider
from discgolfspider.spiders.discsor_spider import DiscsorSpider
from discgolfspider.spiders.frisbeebutikken_spider import FrisbeebutikkenSpider
from discgolfspider.spiders.frisbeesor_spider import FrisbeesorSpider
from discgolfspider.spiders.golfkongen_spider import GolfkongenSpider
from discgolfspider.spiders.kastmeg_spider import KastmegSpider
from discgolfspider.spiders.prodisc_spider import ProdiscSpider
from discgolfspider.spiders.wearediscgolf_spider import WeAreDiscgolfSpider

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
settings = get_project_settings()
configure_logging(settings)
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl():
    logger.info("Starting crawl cycle...")
    
    try:
        runner = CrawlerRunner(settings)
        yield runner.crawl(AceshopSpider)
        yield runner.crawl(ChickWithDiscsSpider)
        yield runner.crawl(DgshopSpider)
        yield runner.crawl(DiscgolfdynastySpider)
        yield runner.crawl(DiscshopenSpider)
        yield runner.crawl(DiscsorSpider)
        yield runner.crawl(FrisbeebutikkenSpider)
        yield runner.crawl(FrisbeesorSpider)
        yield runner.crawl(GolfkongenSpider)
        yield runner.crawl(KastmegSpider)
        yield runner.crawl(ProdiscSpider)
        yield runner.crawl(WeAreDiscgolfSpider)

        logger.info("Crawl cycle completed successfully.")

    except Exception as e:
        logger.error(f"Error in crawl cycle: {e}")
        import traceback
        logger.error(traceback.format_exc())


def cb_loop_error(failure):
    logger.error(f"Loop error: {failure}")
    reactor.stop() # only stop on critical errors


def start():
    logger.info("Crawl process is starting.")

    interval = float(os.getenv("CRAWL_INTERVAL", 3600))
    logger.info(f"Will crawl every {interval} seconds ({interval / 60:.1f} minutes).")

    loop = task.LoopingCall(crawl)

    # Start the loop (runs immediately, then every interval)
    loopDeferred = loop.start(interval)

    # Add error handling for the loop
    loopDeferred.addErrback(cb_loop_error)

    try:
        reactor.run()
    except KeyboardInterrupt:
        logger.info("Crawl process interrupted by user. Shutting down...")
        if loop.running:
            loop.stop()


if __name__ == "__main__":
    from twisted.internet import reactor
    start()
