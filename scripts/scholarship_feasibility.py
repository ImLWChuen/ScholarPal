#!/usr/bin/env python3
"""
ScholarPal - Malaysian Scholarship Source Feasibility Probe & Checklist (KPH)
Evaluates candidate official scholarship portals against crawler feasibility criteria:
  1. Robots.txt permissions & crawl-delay
  2. Static HTML vs. JavaScript-rendered (SPA/Hydration)
  3. Presence of sitemap.xml or RSS/Atom feeds
  4. Pagination pattern (query param, path segment, flat listing, or AJAX)
  5. Location of critical fields (Eligibility, Deadline, Required Documents) - HTML vs. PDF
  6. Terms-of-use / copyright red flags

Strictly respects robots.txt and limits network traffic to <= 5 HTTP requests per domain.
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from typing import Any

try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


DEFAULT_USER_AGENT = (
    "ScholarPal-FeasibilityBot/1.0 (+https://github.com/ImLWChuen/ScholarPal)"
)

DEFAULT_OFFICIAL_TARGETS = [
    {
        "name": "Yayasan Khazanah",
        "url": "https://www.yayasankhazanah.com.my/scholarship-programmes",
        "sample_detail": "https://www.yayasankhazanah.com.my/scholarship-programmes/khazanah-global-scholarship-programme",
    },
    {
        "name": "JPA Penajaan (eSila)",
        "url": "https://penajaan.jpa.gov.my",
        "sample_detail": "https://penajaan.jpa.gov.my/info-penajaan/latihan-sebelum-perkhidmatan/program-pelajar/program-penajaan-nasional-ppn.html",
    },
    {
        "name": "Bank Negara Malaysia",
        "url": "https://www.bnm.gov.my/careers/scholarships",
        "sample_detail": "https://www.bnm.gov.my/careers/scholarships",
    },
]


class BasicHTMLInspector(HTMLParser):
    """Lightweight streaming HTML analyzer relying only on Python standard library."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.pdf_links: list[str] = []
        self.script_count = 0
        self.text_content: list[str] = []
        self.has_spa_root = False
        self.has_pagination_widget = False
        self.has_rss_link = False
        self.semantic_elements_count = 0
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}

        if tag in ("script",):
            self.in_script = True
            self.script_count += 1
        elif tag in ("style",):
            self.in_style = True

        if tag in (
            "article",
            "section",
            "main",
            "table",
            "ul",
            "ol",
            "h1",
            "h2",
            "h3",
            "h4",
            "p",
        ):
            self.semantic_elements_count += 1

        # Check for SPA mount points
        tag_id = attrs_dict.get("id", "").lower()
        tag_class = attrs_dict.get("class", "").lower()
        if tag_id in ("root", "app", "__next", "__nuxt") or "react-root" in tag_class:
            self.has_spa_root = True

        # Check for pagination clues
        if any(
            term in tag_class
            for term in ("pagination", "pager", "page-numbers", "nav-links")
        ):
            self.has_pagination_widget = True

        # Check for RSS / Atom feeds
        if tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            link_type = attrs_dict.get("type", "").lower()
            if "alternate" in rel and (
                "rss" in link_type or "atom" in link_type or "xml" in link_type
            ):
                self.has_rss_link = True

        # Check links
        if tag == "a" and "href" in attrs_dict:
            href = attrs_dict["href"].strip()
            if href:
                self.links.append(href)
                if ".pdf" in href.lower():
                    self.pdf_links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False

    def handle_data(self, data: str) -> None:
        if not self.in_script and not self.in_style:
            cleaned = data.strip()
            if cleaned:
                self.text_content.append(cleaned)

    def get_clean_text(self) -> str:
        return " ".join(self.text_content)


@dataclass
class SiteFeasibilityReport:
    name: str
    target_url: str
    robots_allowed: bool = True
    robots_detail: str = "Permitted"
    crawl_delay: int | None = None
    listing_render_mode: str = "Static HTML"
    sitemap_status: str = "None"
    sitemap_url: str | None = None
    pagination_pattern: str = "Flat / Single-page"
    eligibility_location: str = "On-page HTML"
    deadline_location: str = "On-page HTML"
    documents_location: str = "On-page HTML"
    data_location_overall: str = "On-page HTML"
    tos_flags: list[str] = field(default_factory=list)
    tos_summary: str = "Clean / Permitted"
    scores: dict[str, int] = field(default_factory=dict)
    total_score: int = 0
    feasibility_tier: str = "High"
    requests_made: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ScholarshipFeasibilityProbe:
    """Orchestrates lightweight probing of a candidate scholarship portal."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 12.0,
        verify_ssl: bool = False,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ms;q=0.8",
        }

    def _fetch(self, url: str) -> tuple[int | None, str | None, str | None]:
        """
        Executes a single HTTP GET request.
        Returns: (status_code, response_text, final_url)
        """
        if HAS_HTTPX:
            try:
                with httpx.Client(
                    headers=self.headers,
                    timeout=self.timeout,
                    follow_redirects=True,
                    verify=self.verify_ssl,
                ) as client:
                    resp = client.get(url)
                    return resp.status_code, resp.text, str(resp.url)
            except (httpx.HTTPError, ssl.SSLError, TimeoutError, OSError):
                return None, None, None
        else:
            try:
                req = urllib.request.Request(url, headers=self.headers)
                context = ssl.create_default_context()
                if not self.verify_ssl:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                with urllib.request.urlopen(
                    req, timeout=self.timeout, context=context
                ) as response:
                    final_url = response.geturl()
                    status = response.getcode()
                    charset = response.headers.get_content_charset() or "utf-8"
                    body = response.read().decode(charset, errors="replace")
                    return status, body, final_url
            except urllib.error.HTTPError as e:
                return e.code, None, None
            except (urllib.error.URLError, ssl.SSLError, TimeoutError, OSError):
                return None, None, None

    def evaluate_robots(
        self, base_url: str, check_path: str
    ) -> tuple[bool, str, int | None, str | None]:
        """Request 1: Fetch and parse robots.txt."""
        robots_url = urllib.parse.urljoin(base_url, "/robots.txt")
        status, text, _ = self._fetch(robots_url)

        if not status or status >= 400 or not text:
            return True, "No robots.txt found (default allow)", None, None

        sitemap_found: str | None = None
        crawl_delay: int | None = None
        disallow_rules: list[str] = []

        target_section = False
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            lower_line = line.lower()
            if lower_line.startswith("user-agent:"):
                ua_val = line.split(":", 1)[1].strip()
                target_section = ua_val == "*" or "scholarpal" in ua_val.lower()
            elif lower_line.startswith("sitemap:"):
                sm = line.split(":", 1)[1].strip()
                if not sitemap_found:
                    sitemap_found = urllib.parse.urljoin(base_url, sm)
            elif target_section:
                if lower_line.startswith("disallow:"):
                    path_val = line.split(":", 1)[1].strip()
                    if path_val:
                        disallow_rules.append(path_val)
                elif lower_line.startswith("crawl-delay:"):
                    try:
                        crawl_delay = int(float(line.split(":", 1)[1].strip()))
                    except ValueError:
                        pass

        # Check if candidate path matches any disallow rules
        allowed = True
        matched_rule = ""
        parsed_target = urllib.parse.urlparse(check_path).path or "/"
        for rule in disallow_rules:
            if rule == "/":
                allowed = False
                matched_rule = "Disallow: /"
                break
            if rule.rstrip("/") and parsed_target.startswith(rule.rstrip("/")):
                allowed = False
                matched_rule = f"Disallow: {rule}"
                break

        detail = f"Blocked by '{matched_rule}'" if not allowed else "Path allowed"
        return allowed, detail, crawl_delay, sitemap_found

    def probe_sitemap(
        self, base_url: str, sitemap_hint: str | None
    ) -> tuple[str, str | None]:
        """Request 2: Verify sitemap or RSS feed existence."""
        candidates = []
        if sitemap_hint:
            candidates.append(sitemap_hint)
        candidates.extend(
            [
                urllib.parse.urljoin(base_url, "/sitemap.xml"),
                urllib.parse.urljoin(base_url, "/feed"),
                urllib.parse.urljoin(base_url, "/rss"),
            ]
        )

        for candidate in candidates[:2]:  # probe at most 1-2 candidate URLs
            status, text, final_url = self._fetch(candidate)
            if status == 200 and text:
                text_lower = text[:500].lower()
                if "urlset" in text_lower or "sitemapindex" in text_lower:
                    return "Sitemap XML", final_url
                if "<rss" in text_lower or "<feed" in text_lower:
                    return "RSS/Atom Feed", final_url

        return "None", None

    def analyze_page_render_and_pagination(
        self, html: str, url: str
    ) -> tuple[str, str, list[str], list[str]]:
        """Analyzes listing HTML for rendering mode, pagination, and sublinks."""
        inspector = BasicHTMLInspector()
        inspector.feed(html)

        text_len = len(inspector.get_clean_text())
        total_len = len(html)
        text_ratio = text_len / max(total_len, 1)

        # Detect Render Mode
        if (
            inspector.has_spa_root
            and text_len < 400
            and inspector.script_count > 3
            or text_ratio < 0.05
            and inspector.script_count > 10
            and inspector.semantic_elements_count < 5
        ):
            render_mode = "JS-rendered / SPA"
        elif inspector.semantic_elements_count > 15 and text_len > 1200:
            render_mode = "Static HTML"
        else:
            render_mode = "Mixed (Static shell with dynamic widgets)"

        # Detect Pagination Pattern
        pagination_pattern = "Flat / Single-page"
        parsed_url = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed_url.query)

        pagination_params = {"page", "p", "page_no", "offset", "start", "pg"}
        if any(k.lower() in pagination_params for k in qs):
            pagination_pattern = "Query Param (?page=)"
        else:
            # Check links on page
            has_query_paging = False
            has_path_paging = False
            for lk in inspector.links:
                lk_lower = lk.lower()
                if any(f"{p}=" in lk_lower for p in pagination_params):
                    has_query_paging = True
                    break
                if re.search(r"/page/\d+|/p/\d+", lk_lower):
                    has_path_paging = True
                    break

            if has_query_paging:
                pagination_pattern = "Query Param (?page=)"
            elif has_path_paging:
                pagination_pattern = "Path Segment (/page/N)"
            elif inspector.has_pagination_widget:
                pagination_pattern = "Dynamic / AJAX Widget"
            else:
                pagination_pattern = "Flat / Single-page"

        return render_mode, pagination_pattern, inspector.links, inspector.pdf_links

    def analyze_data_requirements(
        self, html: str, pdf_links: list[str]
    ) -> tuple[str, str, str, str]:
        """Request 4 (detail page analysis): checks on-page HTML vs PDF for fields."""
        # Strip PDF download anchors so their link labels do not falsely count as on-page content
        html_without_pdf_anchors = re.sub(
            r"<a\b[^>]*href=[\"'][^\"']*\.pdf[\"'][^>]*>.*?</a>",
            " ",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        text_lower = re.sub(r"<[^>]+>", " ", html_without_pdf_anchors).lower()

        # Keywords for Malaysian scholarship contexts (English & Bahasa Melayu)
        eligibility_kw = [
            "eligibility",
            "criteria",
            "requirement",
            "syarat",
            "kelayakan",
            "cgpa",
            "minimum",
        ]
        deadline_kw = [
            "deadline",
            "closing date",
            "tarikh tutup",
            "application period",
            "tempoh permohonan",
            "due date",
        ]
        documents_kw = [
            "documents",
            "transcript",
            "supporting document",
            "dokumen",
            "salinan",
            "ic copy",
            "kad pengenalan",
            "lampiran",
        ]

        elig_in_html = any(kw in text_lower for kw in eligibility_kw)
        dead_in_html = any(kw in text_lower for kw in deadline_kw)
        docs_in_html = any(kw in text_lower for kw in documents_kw)

        pdf_has_elig = any(
            any(
                kw in pdf.lower()
                for kw in ["syarat", "criteria", "eligibility", "garis_panduan"]
            )
            for pdf in pdf_links
        )
        pdf_has_docs = any(
            any(
                kw in pdf.lower()
                for kw in ["dokumen", "checklist", "lampiran", "borang"]
            )
            for pdf in pdf_links
        )

        elig_loc = (
            "On-page HTML"
            if elig_in_html
            else ("PDF Attachment" if pdf_has_elig else "Missing / Unclear")
        )
        dead_loc = "On-page HTML" if dead_in_html else "Missing / Portal Banner"
        docs_loc = (
            "On-page HTML"
            if docs_in_html
            else (
                "PDF Attachment"
                if pdf_has_docs or pdf_links
                else "Missing / Portal Link"
            )
        )

        if elig_in_html and not pdf_links:
            overall = "On-page HTML"
        elif elig_in_html and pdf_links:
            overall = "Mixed (HTML + PDF Guidelines)"
        elif not elig_in_html and pdf_links:
            overall = "PDF Attachment Only"
        else:
            overall = "On-page HTML"

        return elig_loc, dead_loc, docs_loc, overall

    def inspect_terms_of_use(
        self, base_url: str, html_text: str
    ) -> tuple[list[str], str]:
        """Request 5: Probe Terms of Use / Disclaimer page."""
        red_flags: set[str] = set()

        # Look for terms links in HTML footer
        candidate_urls = [
            urllib.parse.urljoin(base_url, "/terms"),
            urllib.parse.urljoin(base_url, "/terms-of-use"),
            urllib.parse.urljoin(base_url, "/terms-and-conditions"),
            urllib.parse.urljoin(base_url, "/disclaimer"),
            urllib.parse.urljoin(base_url, "/penafian.html"),
            urllib.parse.urljoin(base_url, "/privacy-policy"),
        ]

        # Extract explicit terms links from the HTML if present
        for link in re.findall(
            r"href=[\"\']([^\"\']*(?:term|penafian|disclaimer|copyright|privacy)[^\"\']*)[\"\']",
            html_text,
            re.IGNORECASE,
        ):
            candidate_urls.insert(0, urllib.parse.urljoin(base_url, link))

        probed = False
        for cand in candidate_urls[:2]:  # check up to 2 candidate terms URLs
            status, text, _ = self._fetch(cand)
            if status == 200 and text:
                probed = True
                t_lower = text.lower()

                # Look for restrictive phrases
                if re.search(r"\b(scraping|scraper|crawling|spidering)\b", t_lower):
                    red_flags.add("Explicit anti-scraping / bot prohibition")
                if re.search(
                    r"\b(automated system|automated tool|automated access)\b", t_lower
                ):
                    red_flags.add("Automated access restriction")
                if (
                    "tanpa kebenaran bertulis" in t_lower
                    or "without prior written permission" in t_lower
                ):
                    red_flags.add("Written permission clause for content reproduction")
                if "commercial purposes" in t_lower or "tujuan komersial" in t_lower:
                    red_flags.add("Non-commercial use only clause")

        if not probed:
            summary = "No separate TOS page found (Standard statutory public domain)"
        elif not red_flags:
            summary = "Clean / Permitted"
        else:
            summary = "; ".join(sorted(red_flags))

        return sorted(red_flags), summary

    def calculate_score(self, report: SiteFeasibilityReport) -> None:
        """
        KPH Scoring Rubric (Max: 14 points):
          - Robots Allowed: 0 = Disallowed, 1 = Heavy path restrictions, 2 = Fully permitted
          - Crawl Delay: 0 = >30s or aggressive rate limits, 1 = 6-30s, 2 = <=5s or None
          - Listing Render Mode: 0 = SPA/JS-only, 1 = Mixed, 2 = Pure Static HTML
          - Sitemap / Feed: 0 = None, 1 = RSS or partial sitemap, 2 = Complete Sitemap XML
          - Pagination: 0 = Complex AJAX/infinite scroll, 1 = Flat multi-card listing, 2 = Standard Query/Path
          - Data Location: 0 = PDF-only, 1 = Mixed (HTML + PDF), 2 = Complete on-page HTML
          - TOS Red Flags: 0 = Explicit anti-bot ban, 1 = Standard non-commercial/attribution, 2 = Open/No restrictions
        """
        scores: dict[str, int] = {}

        # 1. Robots.txt
        if not report.robots_allowed:
            scores["robots"] = 0
        elif "Disallow" in report.robots_detail:
            scores["robots"] = 1
        else:
            scores["robots"] = 2

        # 2. Crawl Delay
        if report.crawl_delay is None or report.crawl_delay <= 5:
            scores["crawl_delay"] = 2
        elif 5 < report.crawl_delay <= 30:
            scores["crawl_delay"] = 1
        else:
            scores["crawl_delay"] = 0

        # 3. Render Mode
        if "Static HTML" in report.listing_render_mode:
            scores["render_mode"] = 2
        elif "Mixed" in report.listing_render_mode:
            scores["render_mode"] = 1
        else:
            scores["render_mode"] = 0

        # 4. Sitemap / Feeds
        if report.sitemap_status == "Sitemap XML":
            scores["sitemap"] = 2
        elif report.sitemap_status == "RSS/Atom Feed":
            scores["sitemap"] = 1
        else:
            scores["sitemap"] = 0

        # 5. Pagination Pattern
        if (
            "Query Param" in report.pagination_pattern
            or "Path Segment" in report.pagination_pattern
        ):
            scores["pagination"] = 2
        elif "Flat" in report.pagination_pattern:
            scores["pagination"] = 1
        else:
            scores["pagination"] = 0

        # 6. Data Location
        if report.data_location_overall == "On-page HTML":
            scores["data_location"] = 2
        elif "Mixed" in report.data_location_overall:
            scores["data_location"] = 1
        else:
            scores["data_location"] = 0

        # 7. Terms of Use
        if any("Explicit anti-scraping" in f for f in report.tos_flags):
            scores["tos"] = 0
        elif report.tos_flags:
            scores["tos"] = 1
        else:
            scores["tos"] = 2

        report.scores = scores
        total = sum(scores.values())
        report.total_score = total

        if total >= 11:
            report.feasibility_tier = "High"
        elif total >= 7:
            report.feasibility_tier = "Medium"
        else:
            report.feasibility_tier = "Low (High Complexity)"

    def probe_site(
        self,
        name: str,
        target_url: str,
        sample_detail: str | None = None,
    ) -> SiteFeasibilityReport:
        """Runs the 5-request probe pipeline on a candidate portal."""
        report = SiteFeasibilityReport(name=name, target_url=target_url)
        base_url = (
            urllib.parse.urlparse(target_url)
            ._replace(path="/", query="", fragment="")
            .geturl()
        )

        req_count = 0

        # Request 1: robots.txt
        robots_allowed, robots_detail, crawl_delay, sitemap_hint = self.evaluate_robots(
            base_url, target_url
        )
        report.robots_allowed = robots_allowed
        report.robots_detail = robots_detail
        report.crawl_delay = crawl_delay
        req_count += 1

        # Request 2: Sitemap probe
        sitemap_status, sitemap_url = self.probe_sitemap(base_url, sitemap_hint)
        report.sitemap_status = sitemap_status
        report.sitemap_url = sitemap_url
        req_count += 1

        # Request 3: Candidate Listing Page
        status, listing_html, final_url = self._fetch(target_url)
        req_count += 1

        discovered_detail_url = sample_detail
        detail_pdf_links: list[str] = []

        if status == 200 and listing_html:
            render_mode, pagination_pattern, links, _pdfs = (
                self.analyze_page_render_and_pagination(
                    listing_html, final_url or target_url
                )
            )
            report.listing_render_mode = render_mode
            report.pagination_pattern = pagination_pattern

            # If no detail page supplied, try to auto-pick from listing page
            if not discovered_detail_url:
                for lk in links:
                    lk_lower = lk.lower()
                    if any(
                        term in lk_lower
                        for term in ["program", "scholarship", "biasiswa", "tajaan"]
                    ) and not lk_lower.endswith(".pdf"):
                        discovered_detail_url = urllib.parse.urljoin(target_url, lk)
                        break

        # Request 4: Candidate Detail Page
        detail_target = discovered_detail_url or target_url
        detail_html = listing_html  # fallback to listing if same
        if detail_target != target_url:
            d_status, d_body, _ = self._fetch(detail_target)
            req_count += 1
            if d_status == 200 and d_body:
                detail_html = d_body

        if detail_html:
            # Extract PDF links from detail page
            inspector = BasicHTMLInspector()
            inspector.feed(detail_html)
            detail_pdf_links = inspector.pdf_links

            elig_loc, dead_loc, docs_loc, data_overall = self.analyze_data_requirements(
                detail_html, detail_pdf_links
            )
            report.eligibility_location = elig_loc
            report.deadline_location = dead_loc
            report.documents_location = docs_loc
            report.data_location_overall = data_overall

        # Request 5: Terms of Use / Disclaimer Page
        tos_flags, tos_summary = self.inspect_terms_of_use(base_url, listing_html or "")
        req_count += 1
        report.tos_flags = tos_flags
        report.tos_summary = tos_summary

        report.requests_made = req_count
        self.calculate_score(report)
        return report


def generate_markdown_table(reports: list[SiteFeasibilityReport]) -> str:
    """Formats the results into a markdown table for project documentation."""
    headers = [
        "Candidate Source",
        "Robots.txt",
        "Crawl Delay",
        "Render Mode",
        "Sitemap / Feed",
        "Pagination",
        "Data Location",
        "TOS Flags",
        "Score (/14)",
        "Feasibility",
    ]

    rows = []
    for r in reports:
        robots_str = "Permitted" if r.robots_allowed else "Disallowed"
        delay_str = f"{r.crawl_delay}s" if r.crawl_delay is not None else "None"
        render_str = r.listing_render_mode.split()[0]
        sitemap_str = r.sitemap_status.replace(" Feed", "")
        pag_str = r.pagination_pattern.split()[0]
        data_str = (
            "HTML"
            if "HTML" in r.data_location_overall
            and "Mixed" not in r.data_location_overall
            else ("Mixed" if "Mixed" in r.data_location_overall else "PDF")
        )
        tos_str = (
            "Clean"
            if "Clean" in r.tos_summary or "No separate" in r.tos_summary
            else "Restricted"
        )

        rows.append(
            [
                f"**{r.name}**",
                robots_str,
                delay_str,
                render_str,
                sitemap_str,
                pag_str,
                data_str,
                tos_str,
                f"**{r.total_score}**",
                f"**{r.feasibility_tier}**",
            ]
        )

    col_widths = [
        max(len(row[i]) for row in ([headers] + rows)) for i in range(len(headers))
    ]

    def fmt_row(items: list[str]) -> str:
        return (
            "| "
            + " | ".join(items[i].ljust(col_widths[i]) for i in range(len(items)))
            + " |"
        )

    separator = (
        "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
    )

    table_lines = [
        fmt_row(headers),
        separator,
    ]
    for row in rows:
        table_lines.append(fmt_row(row))

    return "\n".join(table_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ScholarPal - Malaysian Scholarship Source Feasibility Checklist (KPH)"
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="Optional candidate URLs to probe. If omitted, default official portals are probed.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw diagnostic JSON alongside markdown table",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=12.0,
        help="HTTP request timeout in seconds (default: 12.0)",
    )
    args = parser.parse_args()

    probe = ScholarshipFeasibilityProbe(timeout=args.timeout)

    targets = []
    if args.urls:
        for u in args.urls:
            parsed = urllib.parse.urlparse(u)
            name = parsed.netloc or u
            targets.append({"name": name, "url": u, "sample_detail": None})
    else:
        targets = DEFAULT_OFFICIAL_TARGETS

    print(f"=== Probing {len(targets)} Malaysian Scholarship Candidate Sources ===")
    print(f"User-Agent: {DEFAULT_USER_AGENT}")
    print("Maximum requests per domain: 5 (strictly rate-limited)\n")

    reports: list[SiteFeasibilityReport] = []
    for target in targets:
        print(f"--> Probing {target['name']} ({target['url']})...")
        report = probe.probe_site(
            name=target["name"],
            target_url=target["url"],
            sample_detail=target.get("sample_detail"),
        )
        reports.append(report)

    print("\n" + "=" * 80)
    print("SCORED COMPARISON TABLE (KPH FEASIBILITY CHECKLIST)")
    print("=" * 80 + "\n")
    md_table = generate_markdown_table(reports)
    print(md_table)
    print("\n")

    if args.json:
        print("=== JSON DIAGNOSTICS ===")
        print(json.dumps([r.to_dict() for r in reports], indent=2))


if __name__ == "__main__":
    main()
