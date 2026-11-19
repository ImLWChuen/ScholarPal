"""
Base spider template for Malaysian scholarship portals.
"""

from datetime import datetime, timezone
import scrapy

from crawler.items import RawScholarshipItem


class BaseScholarshipSpider(scrapy.Spider):
    name = "base_scholarship"
    allowed_domains = ["example.com.my"]
    start_urls = ["https://example.com.my/scholarships"]

    def parse(self, response):
        item = RawScholarshipItem()
        item["source_url"] = response.url
        item["provider_name"] = "Example Provider"
        item["raw_html"] = response.text
        item["extracted_title"] = response.css("title::text").get(default="").strip()
        item["crawled_at"] = datetime.now(timezone.utc).isoformat()
        item["http_status"] = response.status
        item["freshness"] = "fresh"
        yield item
