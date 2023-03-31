# from datetime import datetime, timedelta
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import logger, configure_logging
from scrapy.spiderloader import SpiderLoader



from discgolfspider.spiders.sendeskive_spider import SendeskiveSpider
from discgolfspider.spiders.starframe_spider import StarframeSpider


class CrawlScheduler:
    def __init__(self):
        self.settings = get_project_settings()
        
        # Configure logging
        configure_logging({"LOG_LEVEL": self.settings.get("LOG_LEVEL")})

        # Get all spiders
        spider_loader = SpiderLoader.from_settings(self.settings)
        spider_names = spider_loader.list()
        self.spiders = [spider_loader.load(name) for name in spider_names]
        
        logger.info(f"Found spiders: {spider_names}")
        

    def run_crawler(self):
        logger.info("Running crawlers")

        # Create runner
        runner = CrawlerRunner(self.settings)

        # Create a list of deferred objects, one for each spider
        deferreds = [runner.crawl(spider) for spider in self.spiders]

        # When all the deffered objects are done, stop the reactor
        list_of_deferreds = defer.DeferredList(deferreds)
        list_of_deferreds.addBoth(lambda _: reactor.stop())

        # Start the reactor
        reactor.run()

        # # add spdiers to crawl
        # self.runner.crawl(SendeskiveSpider)
        # self.runner.crawl(StarframeSpider)

        # # start crawl
        # deffered = self.runner.join()
        # deffered.addBoth(lambda _: reactor.stop())
        # reactor.run()

    # @staticmethod
    # def get_seconds_until_next_full_hour():
    #     now = datetime.now()
    #     next_full_hour = now + timedelta(hours=1)
    #     next_full_hour = next_full_hour.replace(minute=0, second=0, microsecond=0)
    #     return (next_full_hour - now).total_seconds()

    # def schedule_next_crawl(self):
    #     self.logger.info("Scheduling next crawl")

    #     seconds_until_next_full_hour = self.get_seconds_until_next_full_hour()
    #     task.deferLater(reactor, seconds_until_next_full_hour, self.run_crawl)

    # def run_crawl(self):
    #     self.logger.info("Running crawl")

    #     crawl_deffered = crawl()
    #     crawl_deffered.addBoth(lambda _: self.schedule_next_crawl())

    # def start(self):
    # self.logger.info(f"Crawl process is starting.")

    # # Calculate seconds until next whole hour
    # seconds_until_next_hour = self.get_seconds_until_next_hour()

    # # Check if at least 15 minutes are left until the next whole hour
    # if seconds_until_next_hour >= 15 * 60:
    #     self.run_crawl()  # Run the first crawl immediately
    # else:
    #     # Schedule the first crawl at the second whole hour
    #     task.deferLater(reactor, seconds_until_next_hour + 3600, self.run_crawl)

    # reactor.run()
