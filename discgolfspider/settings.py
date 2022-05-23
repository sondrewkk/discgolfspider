import os

# Scrapy settings for discgolfspider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "discgolfspider"

SPIDER_MODULES = ["discgolfspider.spiders"]
NEWSPIDER_MODULE = "discgolfspider.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "discinstock_crawler (+http://www.discinstock.no)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'discgolfspider.middlewares.DiscgolfspiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 100,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "discgolfspider.pipelines.DiscItemPipeline": 300,
    "discgolfspider.pipelines.DiscItemBrandPipeline": 301,
    "discgolfspider.pipelines.UpdateDiscPipeline": 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Crawl interval
CRAWL_INTERVAL = int(os.getenv("CRAWL_INTERVAL", 3600))  # One hour default

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8080")
API_USERNAME = "discinstock"
API_PASSWORD = "Passw0rd"

API_USERNAME_FILE = os.getenv("API_USERNAME_FILE")
if API_USERNAME_FILE:
    with open(API_USERNAME_FILE, "r") as file:
        API_USERNAME = file.read()

API_PASSWORD_FILE = os.getenv("API_PASSWORD_FILE")
if API_PASSWORD_FILE:
    with open(API_PASSWORD_FILE, "r") as file:
        API_PASSWORD = file.read()

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

# Guru auth
GURU_API_KEY = "changeme"
GURU_API_SECRET = "changeme"

GURU_API_KEY_FILE = os.getenv("GURU_API_KEY_FILE")
if GURU_API_KEY_FILE:
    with open(GURU_API_KEY_FILE, "r") as file:
        GURU_API_KEY = file.read()

GURU_API_SECRET_FILE = os.getenv("GURU_API_SECRET_FILE")
if GURU_API_SECRET_FILE:
    with open(GURU_API_SECRET_FILE, "r") as file:
        GURU_API_SECRET = file.read()
