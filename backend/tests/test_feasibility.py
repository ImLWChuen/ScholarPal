from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so scripts can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.scholarship_feasibility import (  # noqa: E402
    BasicHTMLInspector,
    ScholarshipFeasibilityProbe,
    SiteFeasibilityReport,
    generate_markdown_table,
)


def test_html_inspector_static_render():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Portal</title></head>
    <body>
        <main>
            <h1>Scholarship Programmes 2026</h1>
            <p>Welcome to our scholarship program offering financial assistance to students.</p>
            <article>
                <h2>National Undergraduate Award</h2>
                <p>Full tuition and living allowance provided for eligible candidates.</p>
                <a href="/scholarships/national-undergrad">Read More</a>
                <a href="/docs/handbook.pdf">Download Guidelines</a>
            </article>
        </main>
    </body>
    </html>
    """
    inspector = BasicHTMLInspector()
    inspector.feed(html)
    assert not inspector.has_spa_root
    assert len(inspector.links) == 2
    assert len(inspector.pdf_links) == 1
    assert "Download Guidelines" in inspector.get_clean_text()


def test_html_inspector_spa_detection():
    spa_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Single Page App</title></head>
    <body>
        <div id="root"></div>
        <script src="/static/js/bundle.js"></script>
        <script src="/static/js/vendor.js"></script>
        <script src="/static/js/chunk1.js"></script>
        <script src="/static/js/chunk2.js"></script>
    </body>
    </html>
    """
    probe = ScholarshipFeasibilityProbe()
    render_mode, pagination, _, _ = probe.analyze_page_render_and_pagination(
        spa_html, "https://example.com/scholarships"
    )
    assert "JS-rendered / SPA" in render_mode
    assert pagination == "Flat / Single-page"


def test_pagination_pattern_detection():
    probe = ScholarshipFeasibilityProbe()

    # Query param pagination
    paged_html = '<a href="/scholarships?page=2">Next</a>'
    _, pag_query, _, _ = probe.analyze_page_render_and_pagination(
        paged_html, "https://example.com/scholarships"
    )
    assert "Query Param" in pag_query

    # Path segment pagination
    path_html = '<a href="/scholarships/page/2">Next</a>'
    _, pag_path, _, _ = probe.analyze_page_render_and_pagination(
        path_html, "https://example.com/scholarships"
    )
    assert "Path Segment" in pag_path


def test_analyze_data_requirements_on_page():
    probe = ScholarshipFeasibilityProbe()
    html = """
    <div>
        <h3>Syarat Kelayakan (Eligibility Criteria)</h3>
        <p>Minimum CGPA 3.50 or equivalent in SPM / STPM.</p>
        <h3>Tarikh Tutup (Deadline)</h3>
        <p>Closing date: 31 March 2026</p>
        <h3>Dokumen Diperlukan (Supporting Documents)</h3>
        <p>Please prepare certified true copy of IC and academic transcripts.</p>
    </div>
    """
    elig, dead, docs, overall = probe.analyze_data_requirements(html, [])
    assert elig == "On-page HTML"
    assert dead == "On-page HTML"
    assert docs == "On-page HTML"
    assert overall == "On-page HTML"


def test_analyze_data_requirements_pdf_fallback():
    probe = ScholarshipFeasibilityProbe()
    html = """
    <div>
        <h3>Program Penajaan Pendidikan</h3>
        <p>Sila muat turun garis panduan permohonan melalui pautan di bawah.</p>
        <a href="/downloads/syarat_kelayakan_2026.pdf">Garis Panduan & Syarat Kelayakan</a>
        <a href="/downloads/checklist_dokumen.pdf">Senarai Semak Dokumen</a>
    </div>
    """
    pdfs = ["/downloads/syarat_kelayakan_2026.pdf", "/downloads/checklist_dokumen.pdf"]
    elig, _, docs, overall = probe.analyze_data_requirements(html, pdfs)
    assert elig == "PDF Attachment"
    assert docs == "PDF Attachment"
    assert "PDF" in overall


def test_score_calculation_high_feasibility():
    probe = ScholarshipFeasibilityProbe()
    report = SiteFeasibilityReport(
        name="Test Permitted Static Portal",
        target_url="https://portal.example.com/scholarships",
        robots_allowed=True,
        robots_detail="Path allowed",
        crawl_delay=2,
        listing_render_mode="Static HTML",
        sitemap_status="Sitemap XML",
        pagination_pattern="Query Param (?page=)",
        data_location_overall="On-page HTML",
        tos_flags=[],
        tos_summary="Clean / Permitted",
    )
    probe.calculate_score(report)
    assert report.total_score == 14
    assert report.feasibility_tier == "High"


def test_score_calculation_low_feasibility():
    probe = ScholarshipFeasibilityProbe()
    report = SiteFeasibilityReport(
        name="Restricted SPA Portal",
        target_url="https://spa.example.com",
        robots_allowed=False,
        robots_detail="Blocked by Disallow: /",
        crawl_delay=60,
        listing_render_mode="JS-rendered / SPA",
        sitemap_status="None",
        pagination_pattern="Dynamic / AJAX Widget",
        data_location_overall="PDF Attachment Only",
        tos_flags=["Explicit anti-scraping / bot prohibition"],
        tos_summary="Anti-scraping ban",
    )
    probe.calculate_score(report)
    assert report.total_score == 0
    assert "Low" in report.feasibility_tier


def test_generate_markdown_table():
    r1 = SiteFeasibilityReport(
        name="Yayasan Khazanah",
        target_url="https://example.com/1",
        robots_allowed=True,
        listing_render_mode="Static HTML",
        sitemap_status="Sitemap XML",
        pagination_pattern="Flat",
        data_location_overall="On-page HTML",
        total_score=13,
        feasibility_tier="High",
    )
    table = generate_markdown_table([r1])
    assert "| Candidate Source" in table
    assert "Yayasan Khazanah" in table
    assert "**13**" in table
    assert "**High**" in table
