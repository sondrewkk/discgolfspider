import os

from dotenv import load_dotenv

# Scrapy settings for discgolfspider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

load_dotenv()

BOT_NAME = "discgolfspider"

SPIDER_MODULES = ["discgolfspider.spiders"]
NEWSPIDER_MODULE = "discgolfspider.spiders"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "discinstock_crawler (+http://www.discinstock.no)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.3


# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "discgolfspider.middlewares.DiscgolfspiderDownloaderMiddleware": 100,
    "scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware": 200,
}


# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "discgolfspider.pipelines.DiscItemPipeline": 300,
    "discgolfspider.pipelines.DiscItemBrandPipeline": 301,
    "discgolfspider.pipelines.DiscItemFlightSpecPipeline": 302,
    "discgolfspider.pipelines.UpdateDiscPipeline": 400,
}

# Crawl interval
CRAWL_INTERVAL = float(os.getenv("CRAWL_INTERVAL", 3600))  # One hour default

# API Configuration
API_URL = os.getenv("API_URL")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

API_USERNAME_FILE = os.getenv("API_USERNAME_FILE")
if API_USERNAME_FILE:
    with open(API_USERNAME_FILE, "r") as file:
        API_USERNAME = file.read()

API_PASSWORD_FILE = os.getenv("API_PASSWORD_FILE")
if API_PASSWORD_FILE:
    with open(API_PASSWORD_FILE, "r") as file:
        API_PASSWORD = file.read()

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL")

# Guru auth
WEAREDISCGOLF_API_KEY = os.getenv("WEAREDISCGOLF_API_KEY")
WEAREDISCGOLF_API_SECRET = os.getenv("WEAREDISCGOLF_API_SECRET")

WEAREDISCGOLF_API_KEY_FILE = os.getenv("WEAREDISCGOLF_API_KEY_FILE")
if WEAREDISCGOLF_API_KEY_FILE:
    with open(WEAREDISCGOLF_API_KEY_FILE, "r") as file:
        WEAREDISCGOLF_API_KEY = file.read()

WEAREDISCGOLF_API_SECRET_FILE = os.getenv("WEAREDISCGOLF_API_SECRET_FILE")
if WEAREDISCGOLF_API_SECRET_FILE:
    with open(WEAREDISCGOLF_API_SECRET_FILE, "r") as file:
        WEAREDISCGOLF_API_SECRET = file.read()

# Discshopen auth
DISCSHOPEN_API_KEY = os.getenv("DISCSHOPEN_API_KEY")
DISCSHOPEN_API_SECRET = os.getenv("DISCSHOPEN_API_SECRET")

DISCSHOPEN_API_KEY_FILE = os.getenv("DISCSHOPEN_API_KEY_FILE")
if DISCSHOPEN_API_KEY_FILE:
    with open(DISCSHOPEN_API_KEY_FILE, "r") as file:
        DISCSHOPEN_API_KEY = file.read()

DISCSHOPEN_API_SECRET_FILE = os.getenv("DISCSHOPEN_API_SECRET_FILE")
if DISCSHOPEN_API_SECRET_FILE:
    with open(DISCSHOPEN_API_SECRET_FILE, "r") as file:
        DISCSHOPEN_API_SECRET = file.read()


# Sendeskive auth
SENDESKIVE_API_KEY = os.getenv("SENDESKIVE_API_KEY")

SENDESKIVE_API_KEY_FILE = os.getenv("SENDESKIVE_API_KEY_FILE")
if SENDESKIVE_API_KEY_FILE:
    with open(SENDESKIVE_API_KEY_FILE, "r") as file:
        SENDESKIVE_API_KEY = file.read()

# Prodisc auth
PRODISC_API_KEY = os.getenv("PRODISC_API_KEY")

PRODISC_API_KEY_FILE = os.getenv("PRODISC_API_KEY_FILE")
if PRODISC_API_KEY_FILE:
    with open(PRODISC_API_KEY_FILE, "r") as file:
        PRODISC_API_KEY = file.read()

# Golfkongen auth
GOLFKONGEN_API_KEY = os.getenv("GOLFKONGEN_API_KEY")

GOLFKONGEN_API_KEY_FILE = os.getenv("GOLFKONGEN_API_KEY_FILE")
if GOLFKONGEN_API_KEY_FILE:
    with open(GOLFKONGEN_API_KEY_FILE, "r") as file:
        GOLFKONGEN_API_KEY = file.read()

# Kastmeg auth
KASTMEG_API_KEY = os.getenv("KASTMEG_API_KEY")

KASTMEG_API_KEY_FILE = os.getenv("KASTMEG_API_KEY_FILE")
if KASTMEG_API_KEY_FILE:
    with open(KASTMEG_API_KEY_FILE, "r") as file:
        KASTMEG_API_KEY = file.read()

# Discsor auth
DISCSOR_API_KEY = os.getenv("DISCSOR_API_KEY")

DISCSOR_API_KEY_FILE = os.getenv("DISCSOR_API_KEY_FILE")
if DISCSOR_API_KEY_FILE:
    with open(DISCSOR_API_KEY_FILE, "r") as file:
        DISCSOR_API_KEY = file.read()

# Discgolfwheelie auth
DISCGOLFWHEELIE_API_KEY = os.getenv("DISCGOLFWHEELIE_API_KEY")

DISCGOLFWHEELIE_API_KEY_FILE = os.getenv("DISCGOLFWHEELIE_API_KEY_FILE")
if DISCGOLFWHEELIE_API_KEY_FILE:
    with open(DISCGOLFWHEELIE_API_KEY_FILE, "r") as file:
        DISCGOLFWHEELIE_API_KEY = file.read()

CHICKSWITHDISCS_API_KEY = os.getenv("CHICKSWITHDISCS_API_KEY")

CHICKSWITHDISCS_API_KEY_FILE = os.getenv("CHICKSWITHDISCS_API_KEY_FILE")
if CHICKSWITHDISCS_API_KEY_FILE:
    with open(CHICKSWITHDISCS_API_KEY_FILE, "r") as file:
        CHICKSWITHDISCS_API_KEY = file.read()

# BounceBackBirdie auth
BOUNCEBACKBIRDIE_API_KEY = os.getenv("BOUNCEBACKBIRDIE_API_KEY")

BOUNCEBACKBIRDIE_API_KEY_FILE = os.getenv("BOUNCEBACKBIRDIE_API_KEY_FILE")
if BOUNCEBACKBIRDIE_API_KEY_FILE:
    with open(BOUNCEBACKBIRDIE_API_KEY_FILE, "r") as file:
        BOUNCEBACKBIRDIE_API_KEY = file.read()

# Pipeline flags
ENABLE_DISC_ITEM_FLIGHT_SPEC_PIPELINE = os.getenv("ENABLE_DISC_ITEM_FLIGHT_SPEC_PIPELINE") == "True"
