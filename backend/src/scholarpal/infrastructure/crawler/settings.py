BOT_NAME = "scholarpal"
SPIDER_MODULES = ["scholarpal.infrastructure.crawler.spiders"]

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2
AUTOTHROTTLE_ENABLED = True
