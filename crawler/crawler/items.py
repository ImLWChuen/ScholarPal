"""
Scrapy Item definitions for crawled scholarship documents.
"""

import scrapy


class RawScholarshipItem(scrapy.Item):
    source_url = scrapy.Field()
    provider_name = scrapy.Field()
    raw_html = scrapy.Field()
    extracted_text = scrapy.Field()
    extracted_title = scrapy.Field()
    crawled_at = scrapy.Field()
    http_status = scrapy.Field()
    freshness = scrapy.Field()  # "fresh" or "uncertain"
