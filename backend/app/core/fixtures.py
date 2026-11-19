"""
ScholarPal Test & Demo Fixtures.

Contains:
- 5 Monitored Malaysian Scholarship Sources
- 2 Fictional Administrators
- 5 Student Profiles covering critical boundary cases:
    1. Income exactly at threshold (RM 4,800 B40 ceiling)
    2. Missing fields (Rule 5 compliant NULLs for income and CGPA)
    3. Unmet mandatory rule (CGPA 3.48 vs 3.50 cutoff)
    4. Subject results boundary (7 A/A+ when 8 required)
    5. Study level & citizenship mismatch (Postgraduate international in undergraduate track)
- 15 Realistic but Clearly Fictional Scholarships across all study levels:
    - Secondary / SPM (3)
    - Pre-University / STPM / Foundation (4)
    - Undergraduate (5)
    - Postgraduate / Master's & PhD (3)
All fictional records are explicitly marked with demo flags (status='demo', is_demo=True,
'[DEMO FICTIONAL]' title prefix, and demo URLs) so they NEVER appear as current opportunities.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.profile_preparation.models import UserRole
from app.domain.scholarship_discovery.models import VersionStatus

DEMO_FLAG: bool = True
DEMO_STATUS: str = "demo"
DEMO_FRESHNESS: str = "demo_fixture"
DEMO_PORTAL_BASE: str = "https://demo.scholarpal.internal/fictional-scholarships"

# ---------------------------------------------------------------------------
# 1. SOURCES (5 Monitored Malaysian Scholarship Sponsors)
# ---------------------------------------------------------------------------

FIXTURE_SOURCES: list[dict[str, Any]] = [
    {
        "id": "src-yayasan-khazanah",
        "name": "Yayasan Khazanah",
        "base_url": "https://www.yayasankhazanah.com.my",
        "config": {"is_demo": DEMO_FLAG, "crawl_delay": 2, "timeout": 15},
        "schedule": "0 2 * * *",
        "is_active": True,
    },
    {
        "id": "src-jpa-penajaan",
        "name": "JPA Penajaan (eSila)",
        "base_url": "https://penajaan.jpa.gov.my",
        "config": {"is_demo": DEMO_FLAG, "crawl_delay": 3, "timeout": 20},
        "schedule": "0 3 * * *",
        "is_active": True,
    },
    {
        "id": "src-bank-negara-malaysia",
        "name": "Bank Negara Malaysia",
        "base_url": "https://www.bnm.gov.my",
        "config": {"is_demo": DEMO_FLAG, "crawl_delay": 2, "timeout": 15},
        "schedule": "0 4 * * *",
        "is_active": True,
    },
    {
        "id": "src-yayasan-petronas",
        "name": "Yayasan PETRONAS",
        "base_url": "https://www.yayasanpetronas.com.my",
        "config": {"is_demo": DEMO_FLAG, "crawl_delay": 2, "timeout": 15},
        "schedule": "0 5 * * *",
        "is_active": True,
    },
    {
        "id": "src-yayasan-sarawak",
        "name": "Yayasan Sarawak",
        "base_url": "https://yayasansarawak.org.my",
        "config": {"is_demo": DEMO_FLAG, "crawl_delay": 3, "timeout": 20},
        "schedule": "0 6 * * *",
        "is_active": True,
    },
]

# ---------------------------------------------------------------------------
# 2. ADMINISTRATORS (2 Verified Demo Reviewers)
# ---------------------------------------------------------------------------

FIXTURE_ADMINISTRATORS: list[dict[str, Any]] = [
    {
        "id": "admin-demo-faridah",
        "email": "admin.faridah@demo.scholarpal.internal",
        "full_name": "Dr. Faridah binti Kassim (Lead Verification Officer)",
        "role": UserRole.ADMINISTRATOR.value,
        "is_active": True,
        "is_verified": True,
    },
    {
        "id": "admin-demo-tan",
        "email": "admin.tanwm@demo.scholarpal.internal",
        "full_name": "Ir. Tan Wei Meng (Senior Criteria Auditor)",
        "role": UserRole.ADMINISTRATOR.value,
        "is_active": True,
        "is_verified": True,
    },
]

# ---------------------------------------------------------------------------
# 3. STUDENT PROFILES (5 Boundary Case Personas)
# ---------------------------------------------------------------------------

FIXTURE_STUDENT_USERS: list[dict[str, Any]] = [
    {
        "id": "usr-demo-income-boundary",
        "email": "harith.boundary@demo.scholarpal.internal",
        "full_name": "Muhammad Harith bin Rosli",
        "role": UserRole.STUDENT.value,
        "is_active": True,
        "is_verified": True,
    },
    {
        "id": "usr-demo-missing-fields",
        "email": "izzah.missing@demo.scholarpal.internal",
        "full_name": "Nurul Izzah binti Kamarudin",
        "role": UserRole.STUDENT.value,
        "is_active": True,
        "is_verified": True,
    },
    {
        "id": "usr-demo-unmet-mandatory",
        "email": "daniel.unmet@demo.scholarpal.internal",
        "full_name": "Daniel Tan Boon Teck",
        "role": UserRole.STUDENT.value,
        "is_active": True,
        "is_verified": True,
    },
    {
        "id": "usr-demo-grades-boundary",
        "email": "priya.grades@demo.scholarpal.internal",
        "full_name": "Priya a/p Subramaniam",
        "role": UserRole.STUDENT.value,
        "is_active": True,
        "is_verified": True,
    },
    {
        "id": "usr-demo-mismatch",
        "email": "liam.mismatch@demo.scholarpal.internal",
        "full_name": "Liam Chen Zhi Kang",
        "role": UserRole.STUDENT.value,
        "is_active": True,
        "is_verified": True,
    },
]

FIXTURE_STUDENT_PROFILES: list[dict[str, Any]] = [
    # Boundary 1: Income exactly at threshold (RM 4,800 B40 ceiling)
    {
        "id": "prof-demo-income-boundary",
        "user_id": "usr-demo-income-boundary",
        "study_level": "Undergraduate",
        "education_level": "Undergraduate",
        "nationality": "Malaysian",
        "citizenship": "Malaysian",
        "state_of_origin": "Kedah",
        "field_of_study": "Computer Science",
        "intended_field": "Cybersecurity & Data Privacy",
        "cgpa": 3.85,
        "household_income": 4800.0,  # Exact threshold boundary
        "academic_results": {
            "Bahasa Melayu": "A+",
            "English": "A",
            "Mathematics": "A+",
            "Additional Mathematics": "A",
            "Physics": "A+",
            "Chemistry": "A",
            "Biology": "A",
            "Sejarah": "A+",
        },
    },
    # Boundary 2: Missing fields (Rule 5 compliant NULLs for income and CGPA)
    {
        "id": "prof-demo-missing-fields",
        "user_id": "usr-demo-missing-fields",
        "study_level": "Undergraduate",
        "education_level": "Undergraduate",
        "nationality": "Malaysian",
        "citizenship": "Malaysian",
        "state_of_origin": "Kelantan",
        "field_of_study": "Mechanical Engineering",
        "intended_field": "Robotics & Automation",
        "cgpa": None,  # Transcripts pending
        "household_income": None,  # Undisclosed / Rule 5 Null
        "academic_results": None,
    },
    # Boundary 3: Unmet mandatory rule (CGPA 3.48 vs 3.50 cutoff)
    {
        "id": "prof-demo-unmet-mandatory",
        "user_id": "usr-demo-unmet-mandatory",
        "study_level": "Undergraduate",
        "education_level": "Undergraduate",
        "nationality": "Malaysian",
        "citizenship": "Malaysian",
        "state_of_origin": "Penang",
        "field_of_study": "Civil Engineering",
        "intended_field": "Structural Engineering",
        "cgpa": 3.48,  # Fails mandatory 3.50 requirement by 0.02
        "household_income": 3200.0,
        "academic_results": {
            "Bahasa Melayu": "A",
            "English": "A",
            "Mathematics": "A+",
            "Additional Mathematics": "B+",
            "Physics": "A",
            "Chemistry": "B+",
            "Moral": "A",
        },
    },
    # Boundary 4: Subject results boundary (Exactly 7 A/A+ when 8 required)
    {
        "id": "prof-demo-grades-boundary",
        "user_id": "usr-demo-grades-boundary",
        "study_level": "Pre-University",
        "education_level": "Pre-University",
        "nationality": "Malaysian",
        "citizenship": "Malaysian",
        "state_of_origin": "Selangor",
        "field_of_study": "Foundation in Science",
        "intended_field": "Biotechnology",
        "cgpa": 3.72,
        "household_income": 6500.0,
        "academic_results": {
            "Bahasa Melayu": "A",
            "English": "A+",
            "Mathematics": "A+",
            "Additional Mathematics": "A",
            "Physics": "A",
            "Chemistry": "A",
            "Biology": "A",
            "Sejarah": "B+",  # Exactly 7 A/A+ grades (1 grade short of 8)
        },
    },
    # Boundary 5: Study level & citizenship mismatch
    # (Postgraduate international in undergraduate track)
    {
        "id": "prof-demo-mismatch",
        "user_id": "usr-demo-mismatch",
        "study_level": "Postgraduate",
        "education_level": "Postgraduate",
        "nationality": "Singaporean",
        "citizenship": "Non-Malaysian",
        "state_of_origin": "International",
        "field_of_study": "Fine Arts & Philosophy",
        "intended_field": "Comparative Literature",
        "cgpa": 3.95,
        "household_income": 16000.0,
        "academic_results": {
            "Literature in English": "A+",
            "General Paper": "A",
            "History": "A",
        },
    },
]

# ---------------------------------------------------------------------------
# 4. 15 FICTIONAL SCHOLARSHIPS ACROSS STUDY LEVELS
# ---------------------------------------------------------------------------

FIXTURE_SCHOLARSHIPS: list[dict[str, Any]] = [
    # --- SECONDARY / SPM LEVEL (3 Scholarships) ---
    {
        "id": "sch-demo-sec-01",
        "source_id": "src-yayasan-khazanah",
        "title": "[DEMO FICTIONAL] Yayasan Melati Biasiswa Bakti Menengah 2026",
        "provider": "Yayasan Khazanah (Fictional Secondary Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/yayasan-melati-menengah",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-sec-02",
        "source_id": "src-jpa-penajaan",
        "title": "[DEMO FICTIONAL] Biasiswa Tunas Harapan Sains MARA (Simulated)",
        "provider": "JPA Penajaan (Fictional SBP Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/tunas-harapan-sains",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-sec-03",
        "source_id": "src-yayasan-sarawak",
        "title": "[DEMO FICTIONAL] Tabung Pendidikan Anak Watan Secondary Excellence Award",
        "provider": "Yayasan Sarawak (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/anak-watan-secondary",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    # --- PRE-UNIVERSITY / STPM / FOUNDATION LEVEL (4 Scholarships) ---
    {
        "id": "sch-demo-preu-04",
        "source_id": "src-bank-negara-malaysia",
        "title": "[DEMO FICTIONAL] Biasiswa Pra-Universiti Yayasan Cemerlang Malaysia 2026",
        "provider": "Bank Negara Malaysia (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/prau-cemerlang-malaysia",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-preu-05",
        "source_id": "src-yayasan-khazanah",
        "title": "[DEMO FICTIONAL] Yayasan Khazanah Fictional Pre-U Global Foundation",
        "provider": "Yayasan Khazanah (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/khazanah-preu-foundation",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-preu-06",
        "source_id": "src-jpa-penajaan",
        "title": "[DEMO FICTIONAL] Tabung Warisan Biasiswa Matrikulasi & STPM Madani",
        "provider": "JPA Penajaan (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/matrikulasi-stpm-madani",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-preu-07",
        "source_id": "src-bank-negara-malaysia",
        "title": "[DEMO FICTIONAL] Bank Pembangunan Simulated Pre-University Commerce Bursary",
        "provider": "Bank Negara Malaysia (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/preu-commerce-bursary",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    # --- UNDERGRADUATE LEVEL (5 Scholarships) ---
    {
        "id": "sch-demo-ug-08",
        "source_id": "src-yayasan-petronas",
        "title": "[DEMO FICTIONAL] Yayasan Inovasi Digital Malaysia Tech Apprenticeship 2026",
        "provider": "Yayasan PETRONAS (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/digital-tech-apprenticeship",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-ug-09",
        "source_id": "src-yayasan-petronas",
        "title": "[DEMO FICTIONAL] Yayasan PETRONAS Simulated Green Energy Undergraduate Award",
        "provider": "Yayasan PETRONAS (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/green-energy-award",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-ug-10",
        "source_id": "src-yayasan-khazanah",
        "title": "[DEMO FICTIONAL] Biasiswa Kepimpinan Korporat GLC Watan 2026",
        "provider": "Yayasan Khazanah (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/kepimpinan-glc-watan",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-ug-11",
        "source_id": "src-jpa-penajaan",
        "title": "[DEMO FICTIONAL] Tabung Amanah Siswa B40 Keusahawanan & Perakaunan",
        "provider": "JPA Penajaan (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/siswa-b40-perakaunan",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-ug-12",
        "source_id": "src-yayasan-khazanah",
        "title": "[DEMO FICTIONAL] Biasiswa Khazanah Lestari Undergraduate Merit Award (Simulated)",
        "provider": "Yayasan Khazanah (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/khazanah-lestari-merit",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    # --- POSTGRADUATE / MASTER'S & PHD LEVEL (3 Scholarships) ---
    {
        "id": "sch-demo-pg-13",
        "source_id": "src-yayasan-petronas",
        "title": "[DEMO FICTIONAL] Geran Penyelidikan Sarjana Kecerdasan Buatan Kebangsaan 2026",
        "provider": "Yayasan PETRONAS (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/geran-sarjana-ai",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-pg-14",
        "source_id": "src-yayasan-khazanah",
        "title": "[DEMO FICTIONAL] Yayasan Khazanah Fictional Doctoral Leadership Fellowship",
        "provider": "Yayasan Khazanah (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/khazanah-doctoral-fellowship",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-demo-pg-15",
        "source_id": "src-yayasan-petronas",
        "title": (
            "[DEMO FICTIONAL] Biasiswa Pascasiswazah Kelestarian Alam Sekitar PETRONAS (Simulated)"
        ),
        "provider": "Yayasan PETRONAS (Fictional Track)",
        "official_portal_url": f"{DEMO_PORTAL_BASE}/pascasiswazah-kelestarian",
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": DEMO_STATUS,
        "freshness": DEMO_FRESHNESS,
        "last_verified_at": datetime.now(UTC),
    },
]

# ---------------------------------------------------------------------------
# 5. SCHOLARSHIP VERSIONS (1 per Fictional Scholarship, with Demo Flags)
# ---------------------------------------------------------------------------

FIXTURE_SCHOLARSHIP_VERSIONS: list[dict[str, Any]] = [
    # 1. Secondary: Yayasan Melati
    {
        "id": "ver-demo-sec-01-v1",
        "scholarship_id": "sch-demo-sec-01",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Yayasan Melati Biasiswa Bakti Menengah 2026",
        "description": (
            "Fictional secondary school bursary supporting Form 4-5 students from "
            "lower-income households."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full fees covered",
            "annual_allowance": 3600.0,
            "book_grant": 500.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 2. Secondary: Tunas Harapan MARA
    {
        "id": "ver-demo-sec-02-v1",
        "scholarship_id": "sch-demo-sec-02",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Biasiswa Tunas Harapan Sains MARA (Simulated)",
        "description": "Simulated secondary STEM boarding school excellence award.",
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Boarding & Tuition Fully Sponsored",
            "monthly_stipend": 300.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 3. Secondary: Tabung Anak Watan
    {
        "id": "ver-demo-sec-03-v1",
        "scholarship_id": "sch-demo-sec-03",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Tabung Pendidikan Anak Watan Secondary Excellence Award",
        "description": "Fictional state secondary bursary for Form 5 candidates.",
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full exam fees & allowance",
            "annual_allowance": 2400.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-tan",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 4. Pre-U: Pra-Universiti Cemerlang
    {
        "id": "ver-demo-preu-04-v1",
        "scholarship_id": "sch-demo-preu-04",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Biasiswa Pra-Universiti Yayasan Cemerlang Malaysia 2026",
        "description": "Pre-university full scholarship for premier foundation and A-Levels.",
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full tuition fees",
            "monthly_allowance": 1500.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 5. Pre-U: Khazanah Pre-U
    {
        "id": "ver-demo-preu-05-v1",
        "scholarship_id": "sch-demo-preu-05",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Yayasan Khazanah Fictional Pre-U Global Foundation",
        "description": (
            "Fictional pre-university preparatory sponsorship for elite overseas "
            "undergraduate admission."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full A-Levels college tuition",
            "monthly_allowance": 2500.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 6. Pre-U: Matrikulasi Madani
    {
        "id": "ver-demo-preu-06-v1",
        "scholarship_id": "sch-demo-preu-06",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Tabung Warisan Biasiswa Matrikulasi & STPM Madani",
        "description": (
            "Need-based monthly stipend and textbook grant for public matriculation students."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full institutional fees",
            "monthly_allowance": 1000.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-tan",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 7. Pre-U: Bank Pembangunan Commerce
    {
        "id": "ver-demo-preu-07-v1",
        "scholarship_id": "sch-demo-preu-07",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Bank Pembangunan Simulated Pre-University Commerce Bursary",
        "description": "Commerce and economics preparatory foundation grant.",
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full pre-university tuition",
            "monthly_allowance": 1200.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-tan",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 8. UG: Tech Apprenticeship
    {
        "id": "ver-demo-ug-08-v1",
        "scholarship_id": "sch-demo-ug-08",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Yayasan Inovasi Digital Malaysia Tech Apprenticeship 2026",
        "description": (
            "Fictional full software engineering undergraduate scholarship with tech "
            "apprenticeship."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full undergraduate tuition",
            "monthly_allowance": 3000.0,
            "bond_years": 3,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 9. UG: Green Energy Award
    {
        "id": "ver-demo-ug-09-v1",
        "scholarship_id": "sch-demo-ug-09",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Yayasan PETRONAS Simulated Green Energy Undergraduate Award",
        "description": (
            "Simulated undergraduate scholarship for clean energy and chemical engineering."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full undergraduate tuition",
            "monthly_allowance": 3500.0,
            "bond_years": 5,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 10. UG: Kepimpinan Korporat GLC
    {
        "id": "ver-demo-ug-10-v1",
        "scholarship_id": "sch-demo-ug-10",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Biasiswa Kepimpinan Korporat GLC Watan 2026",
        "description": (
            "Undergraduate corporate finance and economics scholarship with 4-year GLC bond."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full tuition",
            "monthly_allowance": 3200.0,
            "bond_years": 4,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-tan",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 11. UG: Siswa B40 Perakaunan
    {
        "id": "ver-demo-ug-11-v1",
        "scholarship_id": "sch-demo-ug-11",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Tabung Amanah Siswa B40 Keusahawanan & Perakaunan",
        "description": (
            "Need-based full grant for accounting and finance undergraduates from B40 households."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full fees covered",
            "monthly_allowance": 2000.0,
            "bond_years": 0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 12. UG: Khazanah Lestari Merit
    {
        "id": "ver-demo-ug-12-v1",
        "scholarship_id": "sch-demo-ug-12",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Biasiswa Khazanah Lestari Undergraduate Merit Award (Simulated)",
        "description": (
            "Prestigious bond-free merit scholarship for outstanding university scholars."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full tuition fees",
            "monthly_allowance": 4000.0,
            "bond_years": 0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-tan",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 13. PG: Geran Sarjana AI
    {
        "id": "ver-demo-pg-13-v1",
        "scholarship_id": "sch-demo-pg-13",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Geran Penyelidikan Sarjana Kecerdasan Buatan Kebangsaan 2026",
        "description": (
            "National postgraduate research scholarship for Master's by Research in "
            "Artificial Intelligence."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full research tuition",
            "monthly_stipend": 2800.0,
            "research_grant": 10000.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 14. PG: Khazanah Doctoral Fellowship
    {
        "id": "ver-demo-pg-14-v1",
        "scholarship_id": "sch-demo-pg-14",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": "[DEMO FICTIONAL] Yayasan Khazanah Fictional Doctoral Leadership Fellowship",
        "description": "Elite PhD research fellowship tenable at top global institutions.",
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full international PhD fees",
            "monthly_stipend": 6500.0,
            "conference_grant": 15000.0,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-faridah",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
    # 15. PG: Pascasiswazah Kelestarian PETRONAS
    {
        "id": "ver-demo-pg-15-v1",
        "scholarship_id": "sch-demo-pg-15",
        "application_cycle": "2026 Demo Cycle",
        "version_number": 1,
        "title": (
            "[DEMO FICTIONAL] Biasiswa Pascasiswazah Kelestarian Alam Sekitar PETRONAS (Simulated)"
        ),
        "description": (
            "Postgraduate fellowship for sustainability engineering and industrial decarbonisation."
        ),
        "coverage_details": {
            "is_demo": DEMO_FLAG,
            "demo_notice": "FICTIONAL DEMO RECORD - NOT A CURRENT OPPORTUNITY",
            "tuition": "Full postgraduate tuition",
            "monthly_stipend": 3500.0,
            "bond_years": 3,
        },
        "deadline": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-tan",
        "approved_at": datetime.now(UTC),
        "raw_extracted_data": {"is_demo": DEMO_FLAG},
    },
]

# ---------------------------------------------------------------------------
# 6. DETERMINISTIC REQUIREMENTS FOR EACH FICTIONAL SCHOLARSHIP
# ---------------------------------------------------------------------------

FIXTURE_REQUIREMENTS: list[dict[str, Any]] = [
    # sch-demo-sec-01: Yayasan Melati Secondary
    {
        "id": "req-demo-sec-01-income",
        "scholarship_version_id": "ver-demo-sec-01-v1",
        "type": "household_income_max",
        "operator": "lte",
        "value": 4800.0,
        "is_mandatory": True,
        "source_excerpt": "Pendapatan kasar bulanan isi rumah tidak melebihi RM 4,800 sebulan.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-sec-01-nat",
        "scholarship_version_id": "ver-demo-sec-01-v1",
        "type": "nationality",
        "operator": "eq",
        "value": "Malaysian",
        "is_mandatory": True,
        "source_excerpt": "Terbuka kepada warganegara Malaysia sahaja.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-sec-01-lvl",
        "scholarship_version_id": "ver-demo-sec-01-v1",
        "type": "study_level",
        "operator": "in",
        "value": ["Secondary", "SPM"],
        "is_mandatory": True,
        "source_excerpt": (
            "Murid Tingkatan 4 atau Tingkatan 5 di sekolah menengah bantuan kerajaan."
        ),
        "is_subjective": False,
    },
    # sch-demo-sec-02: Tunas Harapan MARA
    {
        "id": "req-demo-sec-02-nat",
        "scholarship_version_id": "ver-demo-sec-02-v1",
        "type": "nationality",
        "operator": "eq",
        "value": "Malaysian",
        "is_mandatory": True,
        "source_excerpt": "Pemohon mestilah warganegara Malaysia.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-sec-02-lvl",
        "scholarship_version_id": "ver-demo-sec-02-v1",
        "type": "study_level",
        "operator": "in",
        "value": ["Secondary", "SPM"],
        "is_mandatory": True,
        "source_excerpt": (
            "Calon sedang mengikuti pengajian aliran Sains Tulen sekolah berasrama penuh."
        ),
        "is_subjective": False,
    },
    # sch-demo-sec-03: Tabung Anak Watan Sarawak
    {
        "id": "req-demo-sec-03-state",
        "scholarship_version_id": "ver-demo-sec-03-v1",
        "type": "state_of_origin",
        "operator": "eq",
        "value": "Sarawak",
        "is_mandatory": True,
        "source_excerpt": (
            "Pemohon atau salah seorang ibu/bapa mestilah anak kelahiran negeri Sarawak."
        ),
        "is_subjective": False,
    },
    {
        "id": "req-demo-sec-03-income",
        "scholarship_version_id": "ver-demo-sec-03-v1",
        "type": "household_income_max",
        "operator": "lte",
        "value": 6000.0,
        "is_mandatory": False,
        "source_excerpt": "Keutamaan pertimbangan kepada keluarga berpendapatan bawah RM 6,000.",
        "is_subjective": False,
    },
    # sch-demo-preu-04: BNM Pra-U Cemerlang
    {
        "id": "req-demo-preu-04-spm",
        "scholarship_version_id": "ver-demo-preu-04-v1",
        "type": "academic_spm",
        "operator": "gte",
        "value": 8,
        "is_mandatory": True,
        "source_excerpt": "Obtained at least 8A's (A/A+) in the SPM examination.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-preu-04-nat",
        "scholarship_version_id": "ver-demo-preu-04-v1",
        "type": "nationality",
        "operator": "eq",
        "value": "Malaysian",
        "is_mandatory": True,
        "source_excerpt": "Strictly open to Malaysian citizens.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-preu-04-lvl",
        "scholarship_version_id": "ver-demo-preu-04-v1",
        "type": "study_level",
        "operator": "in",
        "value": ["Pre-University", "Foundation", "A-Levels"],
        "is_mandatory": True,
        "source_excerpt": "Pursuing full-time accredited Pre-University preparatory programs.",
        "is_subjective": False,
    },
    # sch-demo-preu-05: Khazanah Pre-U Global Foundation
    {
        "id": "req-demo-preu-05-spm",
        "scholarship_version_id": "ver-demo-preu-05-v1",
        "type": "academic_spm",
        "operator": "gte",
        "value": 8,
        "is_mandatory": True,
        "source_excerpt": "Minimum 8A's in SPM with distinction in English and Mathematics.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-preu-05-lead",
        "scholarship_version_id": "ver-demo-preu-05-v1",
        "type": "leadership_assessment",
        "operator": "eq",
        "value": True,
        "is_mandatory": False,
        "source_excerpt": (
            "Demonstrated record of co-curricular leadership and character excellence."
        ),
        "is_subjective": True,
    },
    # sch-demo-preu-06: Matrikulasi Madani
    {
        "id": "req-demo-preu-06-cgpa",
        "scholarship_version_id": "ver-demo-preu-06-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.60,
        "is_mandatory": True,
        "source_excerpt": (
            "Mencapai sekurang-kurangnya PNGK 3.60 dalam semester terkini matrikulasi."
        ),
        "is_subjective": False,
    },
    {
        "id": "req-demo-preu-06-income",
        "scholarship_version_id": "ver-demo-preu-06-v1",
        "type": "household_income_max",
        "operator": "lte",
        "value": 4800.0,
        "is_mandatory": True,
        "source_excerpt": (
            "Dikhaskan bagi pelajar daripada golongan keluarga B40 (pendapatan RM 4,800 ke bawah)."
        ),
        "is_subjective": False,
    },
    # sch-demo-preu-07: Bank Pembangunan Commerce
    {
        "id": "req-demo-preu-07-lvl",
        "scholarship_version_id": "ver-demo-preu-07-v1",
        "type": "study_level",
        "operator": "in",
        "value": ["Pre-University", "Foundation"],
        "is_mandatory": True,
        "source_excerpt": "Full-time foundation or matriculation commerce stream.",
        "is_subjective": False,
    },
    # sch-demo-ug-08: Tech Apprenticeship
    {
        "id": "req-demo-ug-08-cgpa",
        "scholarship_version_id": "ver-demo-ug-08-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.50,
        "is_mandatory": True,
        "source_excerpt": (
            "Possess a minimum current CGPA of 3.50 in computer science or software engineering."
        ),
        "is_subjective": False,
    },
    {
        "id": "req-demo-ug-08-stem",
        "scholarship_version_id": "ver-demo-ug-08-v1",
        "type": "stem_field",
        "operator": "in",
        "value": ["Computer Science", "Software Engineering", "Data Analytics"],
        "is_mandatory": True,
        "source_excerpt": (
            "Course of study must be in Computer Science, Software Engineering, or "
            "Artificial Intelligence."
        ),
        "is_subjective": False,
    },
    # sch-demo-ug-09: PETRONAS Green Energy
    {
        "id": "req-demo-ug-09-academic",
        "scholarship_version_id": "ver-demo-ug-09-v1",
        "type": "academic_cgpa_or_spm",
        "operator": "gte",
        "value": {"cgpa": 3.50, "spm_a_count": 8},
        "is_mandatory": True,
        "source_excerpt": "Minimum CGPA of 3.50 or minimum 8A's in SPM examination.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-ug-09-nat",
        "scholarship_version_id": "ver-demo-ug-09-v1",
        "type": "nationality",
        "operator": "eq",
        "value": "Malaysian",
        "is_mandatory": True,
        "source_excerpt": "Malaysian citizens aged 17 to 23 years.",
        "is_subjective": False,
    },
    # sch-demo-ug-10: Kepimpinan Korporat GLC
    {
        "id": "req-demo-ug-10-cgpa",
        "scholarship_version_id": "ver-demo-ug-10-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.75,
        "is_mandatory": True,
        "source_excerpt": "Possess strong academic credentials with minimum CGPA of 3.75.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-ug-10-income",
        "scholarship_version_id": "ver-demo-ug-10-v1",
        "type": "household_income_max",
        "operator": "lte",
        "value": 12000.0,
        "is_mandatory": False,
        "source_excerpt": (
            "Priority is accorded to applicants from households with monthly "
            "gross income under RM 12,000."
        ),
        "is_subjective": False,
    },
    # sch-demo-ug-11: Siswa B40 Perakaunan
    {
        "id": "req-demo-ug-11-income",
        "scholarship_version_id": "ver-demo-ug-11-v1",
        "type": "household_income_max",
        "operator": "lte",
        "value": 4800.0,
        "is_mandatory": True,
        "source_excerpt": (
            "Pendapatan isi rumah bulanan ibu bapa/penjaga mestilah tidak melebihi "
            "paras RM 4,800 sebulan."
        ),
        "is_subjective": False,
    },
    {
        "id": "req-demo-ug-11-cgpa",
        "scholarship_version_id": "ver-demo-ug-11-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.30,
        "is_mandatory": True,
        "source_excerpt": "Mencapai sekurang-kurangnya PNGK 3.30 bagi semester terkini.",
        "is_subjective": False,
    },
    # sch-demo-ug-12: Khazanah Lestari Merit
    {
        "id": "req-demo-ug-12-cgpa",
        "scholarship_version_id": "ver-demo-ug-12-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.80,
        "is_mandatory": True,
        "source_excerpt": "Outstanding academic record with minimum CGPA of 3.80.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-ug-12-nat",
        "scholarship_version_id": "ver-demo-ug-12-v1",
        "type": "nationality",
        "operator": "eq",
        "value": "Malaysian",
        "is_mandatory": True,
        "source_excerpt": "Malaysian citizenship required.",
        "is_subjective": False,
    },
    # sch-demo-pg-13: Geran Sarjana AI
    {
        "id": "req-demo-pg-13-cgpa",
        "scholarship_version_id": "ver-demo-pg-13-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.65,
        "is_mandatory": True,
        "source_excerpt": "Bachelor's degree with First Class Honours or minimum CGPA of 3.65.",
        "is_subjective": False,
    },
    {
        "id": "req-demo-pg-13-lvl",
        "scholarship_version_id": "ver-demo-pg-13-v1",
        "type": "study_level",
        "operator": "in",
        "value": ["Postgraduate", "Master's"],
        "is_mandatory": True,
        "source_excerpt": (
            "Enrolled in full-time Master's by Research in Artificial Intelligence or Robotics."
        ),
        "is_subjective": False,
    },
    # sch-demo-pg-14: Khazanah Doctoral Fellowship
    {
        "id": "req-demo-pg-14-cgpa",
        "scholarship_version_id": "ver-demo-pg-14-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.85,
        "is_mandatory": True,
        "source_excerpt": (
            "Master's degree CGPA of at least 3.85 with outstanding research thesis publication."
        ),
        "is_subjective": False,
    },
    {
        "id": "req-demo-pg-14-lvl",
        "scholarship_version_id": "ver-demo-pg-14-v1",
        "type": "study_level",
        "operator": "in",
        "value": ["Postgraduate", "PhD"],
        "is_mandatory": True,
        "source_excerpt": (
            "Full-time doctoral research degree candidate at an internationally "
            "accredited university."
        ),
        "is_subjective": False,
    },
    # sch-demo-pg-15: Pascasiswazah Kelestarian PETRONAS
    {
        "id": "req-demo-pg-15-cgpa",
        "scholarship_version_id": "ver-demo-pg-15-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.50,
        "is_mandatory": True,
        "source_excerpt": (
            "Minimum CGPA of 3.50 in engineering, environmental science, or related disciplines."
        ),
        "is_subjective": False,
    },
    {
        "id": "req-demo-pg-15-nat",
        "scholarship_version_id": "ver-demo-pg-15-v1",
        "type": "nationality",
        "operator": "eq",
        "value": "Malaysian",
        "is_mandatory": True,
        "source_excerpt": (
            "Malaysian citizens committed to 3 years industrial research contribution."
        ),
        "is_subjective": False,
    },
]

# ---------------------------------------------------------------------------
# 7. REQUIRED DOCUMENTS FOR FICTIONAL SCHOLARSHIPS
# ---------------------------------------------------------------------------

FIXTURE_DOCUMENTS: list[dict[str, Any]] = [
    {
        "id": "doc-demo-sec-01-cert",
        "scholarship_version_id": "ver-demo-sec-01-v1",
        "name": "Borang Pengesahan Pendapatan Keluarga (JKKK / Majikan)",
        "description": "Salinan slip gaji atau pengesahan pendapatan ibu bapa yang disahkan.",
        "is_mandatory": True,
        "format_instructions": "PDF under 3MB",
    },
    {
        "id": "doc-demo-preu-04-spm",
        "scholarship_version_id": "ver-demo-preu-04-v1",
        "name": "Certified SPM Examination Slip",
        "description": "Official certified statement of SPM examination grades.",
        "is_mandatory": True,
        "format_instructions": "PDF under 5MB with official school stamp",
    },
    {
        "id": "doc-demo-ug-08-trans",
        "scholarship_version_id": "ver-demo-ug-08-v1",
        "name": "Latest University Semester Academic Transcript",
        "description": "Official transcript showing cumulative GPA of at least 3.50.",
        "is_mandatory": True,
        "format_instructions": "Official university portal transcript with QR verification",
    },
    {
        "id": "doc-demo-ug-09-ic",
        "scholarship_version_id": "ver-demo-ug-09-v1",
        "name": "MyKad Certified Copy",
        "description": "Clear front and back copy of Malaysian identity card.",
        "is_mandatory": True,
        "format_instructions": "PDF or JPEG under 2MB",
    },
    {
        "id": "doc-demo-pg-13-prop",
        "scholarship_version_id": "ver-demo-pg-13-v1",
        "name": "Master's Research Proposal (AI & Robotics)",
        "description": "Detailed 5-page research proposal approved by academic supervisor.",
        "is_mandatory": True,
        "format_instructions": "PDF format using IEEE or ACM structure",
    },
    {
        "id": "doc-demo-pg-14-pub",
        "scholarship_version_id": "ver-demo-pg-14-v1",
        "name": "Doctoral Research Dossier & Academic Publications",
        "description": (
            "Comprehensive CV, list of peer-reviewed publications, and university offer letter."
        ),
        "is_mandatory": True,
        "format_instructions": "Consolidated PDF under 10MB",
    },
]
