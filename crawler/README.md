# ScholarPal Crawler

Web crawling and document cleaning pipeline for Malaysian scholarship portals.

## Technologies
- **Scrapy**: High-throughput web crawling framework
- **BeautifulSoup4**: DOM sanitization and fallback content extraction
- **Trafilatura**: Precision main-text and table extraction

## Architecture & Rules
- **Rule 4 Adherence**: In the event of network timeouts, 404s, or parsing failures, spiders never delete or mark scholarships as closed. Instead, the backend freshness monitor retains the last-known state and marks freshness as `uncertain`.

## Usage

1. Install dependencies:
   ```bash
   pip install -e .
   ```
2. Test a spider:
   ```bash
   scrapy crawl base_scholarship
   ```
3. Check available spiders:
   ```bash
   scrapy list
   ```
