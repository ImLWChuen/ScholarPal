"""
Scrapy settings for ScholarPal crawler project.
"""

BOT_NAME = "crawler"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

# Crawl responsibly by identifying yourself (and your website/contact)
USER_AGENT = "ScholarPalBot/0.1 (+https://scholarpal.my/bot; info@scholarpal.my)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 1.0

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "crawler.middlewares.ScholarPalDownloaderMiddleware": 543,
}

# Configure item pipelines
# Cleans raw HTML using BeautifulSoup and trafilatura
ITEM_PIPELINES = {
    "crawler.pipelines.ContentCleaningPipeline": 300,
    "crawler.pipelines.BackendSyncPipeline": 400,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
