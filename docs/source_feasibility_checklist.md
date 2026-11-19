# Source Feasibility Checklist (KPH)
*ScholarPal Web Platform – Malaysian Scholarship Crawler Pipeline*

This document establishes the official source evaluation framework and feasibility analysis for automated ingestion of Malaysian scholarship opportunities into the **ScholarPal** platform.

---

## 1. Executive Summary & Methodology (KPH Framework)

The **KPH** framework evaluates candidate portals across three key dimensions:
1. **Kelayakan (Permissions & Compliance)**: Explicit authorization in `robots.txt`, absence of anti-bot terms-of-use clauses, and acceptable rate-limiting constraints.
2. **Praktikaliti (Extractability & Structure)**: Deterministic crawl discovery via sitemaps/feeds, static HTML rendering vs. JavaScript hydration, predictable pagination, and structured HTML fields vs. unstructured PDF attachments.
3. **Hambatan (Obstacles & Fragility)**: Frequent layout redesigns, transient 404s, missing closing dates, or non-machine-readable scanned attachments.

To balance regulatory authority, coverage across study levels (secondary, pre-university, undergraduate, and postgraduate), and crawler reliability, three official Malaysian scholarship providers were evaluated:
1. **Yayasan Khazanah** (`https://www.yayasankhazanah.com.my`) – Sovereign wealth fund sponsoring global and domestic premier undergraduate and postgraduate awards.
2. **Jabatan Perkhidmatan Awam (JPA Penajaan / eSila)** (`https://penajaan.jpa.gov.my`) – The primary Malaysian federal civil service scholarship authority.
3. **Bank Negara Malaysia (BNM)** (`https://www.bnm.gov.my/careers/scholarships`) – Central bank prestigious scholarship programmes (Kijang Scholarship, Undergraduate Awards).

---

## 2. Evaluation Rubric & Scoring Scheme

The checklist assesses candidate portals across seven criteria. Each criterion is scored on a **0 to 2** scale, yielding an overall score out of **14**:

| Metric | 0 Points | 1 Point | 2 Points |
| :--- | :--- | :--- | :--- |
| **Robots.txt Permission** | Explicitly disallowed for crawler or global user agents (`Disallow: /`) | Restricted paths or ambiguous path wildcards | Allowed for candidate paths (`Disallow:` or no restrictions) |
| **Crawl-delay & Rate Limits** | Aggressive delay (>30s) or active Cloudflare/WAF block | Moderate delay (6s to 30s) | Respectful or standard delay (≤5s or unspecified) |
| **Listing Render Mode** | Client-side SPA (React/Vue/Angular shell requiring headless browser) | Mixed (SSR shell with client-side dynamic widgets) | Server-rendered Static HTML (parseable via Scrapy/BeautifulSoup) |
| **Sitemap / Feeds** | No sitemap or feed found; blind page traversal required | RSS/Atom feed or partial sitemap available | Valid machine-readable `sitemap.xml` available |
| **Pagination Pattern** | Unbounded infinite scroll, obscure POST requests, or encrypted offsets | Flat single-page multi-card listing (no iteration needed) | Standard query parameters (`?page=N`) or path segments (`/page/N`) |
| **Data Location** | Critical requirements isolated inside scanned image PDFs only | Mixed (summary in HTML, complete criteria in PDF attachments) | Complete eligibility, deadlines, and document checklists in on-page HTML |
| **Terms of Use Red Flags** | Explicit contractual ban on scraping, crawlers, or automated harvesting | Standard statutory copyright / non-commercial restriction clause | Clean public domain or permitted automated access with attribution |

### Feasibility Classification Tiers
- **High Feasibility (11 – 14 points)**: Recommended for direct, high-confidence automated crawling using Scrapy, Trafilatura, and BeautifulSoup.
- **Medium Feasibility (7 – 10 points)**: Suitable for crawling; requires fallback parsers or hybrid PDF extraction pipelines.
- **Low Feasibility (0 – 6 points)**: High technical friction or legal risk; requires headless browsers (Playwright) or manual administrator ingestion.

---

## 3. Scored Comparison Table

Results obtained from the live probe script (`scripts/scholarship_feasibility.py`):

| Candidate Source | Robots.txt | Crawl Delay | Render Mode | Sitemap / Feed | Pagination | Data Location | TOS Flags | Score (/14) | Feasibility Tier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Yayasan Khazanah** | Permitted (2) | None (2) | Mixed (1) | Sitemap XML (2) | Flat (1) | HTML (2) | Clean (2) | **12 / 14** | **High** |
| **JPA Penajaan (eSila)** | Permitted (2) | None (2) | Static HTML (2) | None (0) | Query (2) | Mixed (1) | Clean (2) | **11 / 14** | **High** |
| **Bank Negara Malaysia** | Permitted (2) | None (2) | Static HTML (2) | Sitemap XML (2) | Flat (1) | Mixed (1) | Clean (2) | **12 / 14** | **High** |

---

## 4. Deep-Dive Findings per Candidate Source

### 4.1. Yayasan Khazanah
- **Target URL**: `https://www.yayasankhazanah.com.my/scholarship-programmes`
- **Sample Detail URL**: `https://www.yayasankhazanah.com.my/scholarship-programmes/khazanah-global-scholarship-programme`
- **Robots.txt**: `User-agent: *` followed by `Disallow:` (no paths disallowed) and an explicit `SiteMap: https://www.yayasankhazanah.com.my/XTOPIA_sitemap.ashx`.
- **Render Mode**: ASP.NET / XTOPIA CMS. Delivers clean semantic HTML structure (`<section>`, `<article>`, structured headings) that does not require a browser rendering engine.
- **Pagination**: All main programmes (Global, Watan, Lestari) are displayed on a flat listing page with direct links to dedicated programme detail pages.
- **Data Location**: Detailed eligibility criteria (minimum CGPA, SPM grade thresholds, leadership qualifications) are presented in clean on-page HTML tables and accordion panels.
- **Terms of Use**: Standard privacy policy and disclaimer. No anti-bot or anti-scraping prohibitions.

### 4.2. Jabatan Perkhidmatan Awam (JPA Penajaan / eSila)
- **Target URL**: `https://penajaan.jpa.gov.my`
- **Sample Detail URL**: `https://penajaan.jpa.gov.my/info-penajaan/latihan-sebelum-perkhidmatan/program-pelajar/program-penajaan-nasional-ppn.html`
- **Robots.txt**: Standard Joomla configuration. Disallows backend administrative folders (`/administrator/`, `/bin/`, `/cache/`) while leaving public portal paths fully open.
- **Render Mode**: Server-side rendered Joomla CMS. Fast HTML response without client-side hydration delays.
- **Pagination**: Category listings employ standard query string pagination (`?start=10` / `?page=N`).
- **Data Location**: High-level eligibility and descriptions are present in HTML; operational guidelines, document checklists, and application circulars (*Surat Pekeliling*) are linked as downloadable PDF attachments.
- **Terms of Use**: Malaysian government standard public portal disclaimer. Reproduction permitted for educational and non-commercial purposes.

### 4.3. Bank Negara Malaysia (BNM)
- **Target URL**: `https://www.bnm.gov.my/careers/scholarships`
- **Sample Detail URL**: `https://www.bnm.gov.my/careers/scholarships`
- **Robots.txt**: Restricts search internal endpoints (`Disallow: /view.php?*`), while leaving public careers and scholarship portals open. Contains `sitemap.xml`.
- **Render Mode**: Server-rendered Liferay Enterprise Portal. Rich semantic HTML with structured FAQ and accordion tabs.
- **Pagination**: Single cohesive portal page covering Kijang Pre-University, Undergraduate, and Postgraduate schemes without multi-page pagination.
- **Data Location**: Comprehensive eligibility criteria, eligible fields of study, approved university lists, and application cycles are available on-page with supplementary PDF appendices.
- **Terms of Use**: Clean statutory disclaimer. Commercial re-distribution requires written permission; informational caching and reference permissible.

---

## 5. Crawler Architecture & Integration Recommendations

1. **Rule 4 Adherence (Freshness Flagging over Closure)**:
   Per ScholarPal Non-Negotiable Rule 4, when any candidate portal returns HTTP 404, connection timeouts, or structural changes during scheduled spider runs, the backend **must retain the last-known record** and update `freshness = uncertain`. Spiders must **never** automatically mark a scholarship as closed or delete historical records.
2. **Hybrid PDF & HTML Pipeline**:
   While Yayasan Khazanah and BNM provide rich on-page HTML text, JPA provides operational checklists in PDFs. The Scrapy crawler pipeline must incorporate `trafilatura` for HTML content and a PDF extraction step (`pypdf` / `pdfminer.six`) for linked document checklists.
3. **Politeness & Rate-Limiting**:
   - Set Scrapy `DOWNLOAD_DELAY = 2.0` with `AUTOTHROTTLE_ENABLED = True`.
   - Maintain transparent `User-Agent: ScholarPal-Crawler/1.0 (+https://scholarpal.my/bot)`.
4. **Execution**:
   The automated probe can be executed anytime using:
   ```bash
   make feasibility
   # Or directly:
   python scripts/scholarship_feasibility.py
   ```
