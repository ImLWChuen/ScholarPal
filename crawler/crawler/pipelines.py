"""
Item pipelines for ScholarPal crawler.
Cleans crawled documents using BeautifulSoup and trafilatura.
Rule 4: Failed retrieval keeps the last known record and flags uncertain freshness;
it never marks a scholarship closed.
"""

import logging
from bs4 import BeautifulSoup
import trafilatura

logger = logging.getLogger(__name__)


class ContentCleaningPipeline:
    def process_item(self, item, spider):
        raw_html = item.get("raw_html")
        if not raw_html:
            item["extracted_text"] = ""
            return item

        # Extract main article/content using trafilatura
        extracted = trafilatura.extract(
            raw_html,
            include_links=False,
            include_tables=True,
            favor_precision=True,
        )

        if extracted:
            item["extracted_text"] = extracted
        else:
            # Fallback to BeautifulSoup clean text extraction
            soup = BeautifulSoup(raw_html, "html.parser")
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            item["extracted_text"] = soup.get_text(separator="\n", strip=True)

        return item


class BackendSyncPipeline:
    def process_item(self, item, spider):
        # Pipeline stub for passing cleaned content to backend extraction review queue
        logger.info(f"Processed item from {item.get('source_url')}")
        return item
