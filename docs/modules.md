# ScholarPal Business Modules

ScholarPal organizes business logic into six decoupled domain subpackages:

---

## 1. Profile and Preparation (`domain/profile_preparation`)
- **Purpose**: Manages student demographic and academic profiles.
- **Key Concepts**:
  - Educational levels: Malaysian SPM, STPM, Matriculation, Diploma, Undergraduate, Postgraduate.
  - Malaysian state of origin, Bumiputera status, household income bracket (B40 / M40 / T20).
  - Preparation milestones (transcript collation, extracurricular records, essay drafting).
- **Rule Constraints**: Rule 5 (Unknown values stay unknown/null, never zero) & Rule 8 (Strict student ownership).

---

## 2. Scholarship Discovery (`domain/scholarship_discovery`)
- **Purpose**: Enables searching, browsing, and filtering of curated Malaysian scholarships.
- **Key Concepts**:
  - Filter by level of study, field of study, provider type (government like JPA/MARA, GLC, private foundation, university).
  - Freshness indicator (`fresh` vs `uncertain`).
- **Rule Constraints**: Rule 4 (Failed crawls keep the last known record flagged as `uncertain`).

---

## 3. Extraction and Evidence Review (`domain/extraction_review`)
- **Purpose**: Manages the pipeline from crawled raw documents to structured scholarship records and human verification.
- **Key Concepts**:
  - LLM extraction queue (JSON Schema output).
  - Jev by TypeSafe AI evidence audit using the `Choice` primitive.
  - Admin review dashboard for verifying evidence quotes against crawled text.
- **Rule Constraints**: Rule 1 (LLM extracted output is not an eligibility decision) & Rule 3 (Jev assists admin and never auto-publishes).

---

## 4. Eligibility and Change Impact (`domain/eligibility_impact`)
- **Purpose**: Evaluates student eligibility against scholarship rules and calculates impact of profile changes.
- **Key Concepts**:
  - Deterministic evaluation engine.
  - Three-state criterion status: `satisfied`, `unmet`, `unresolved`.
  - Overall status: `Does not meet recorded requirements`, `Needs clarification`, `Meets recorded requirements`.
  - What-If simulations for prospective GPA, course changes, or income variations.
- **Rule Constraints**: Rule 1 (Deterministic rules only), Rule 2 (Three-state requirements), Rule 6 (What-if checks are ephemeral).

---

## 5. Applications and Interviews (`domain/applications_interviews`)
- **Purpose**: Guides students through application preparation, submission milestones, and interview rounds.
- **Key Concepts**:
  - Application kanban: `drafting`, `ready_to_submit`, `submitted_by_student`, `interview_invited`, `completed`.
  - Portal submission checklist, document tracker, interview preparation notes.
- **Rule Constraints**: Rule 7 (Students submit on external provider portals; ScholarPal never auto-marks submitted) & Rule 8 (Strict student ownership).

---

## 6. Comparison (`domain/comparison`)
- **Purpose**: Provides a side-by-side comparative matrix across multiple scholarships.
- **Key Concepts**:
  - Bond duration (years of service required).
  - Monthly allowance / stipend comparison.
  - Tuition coverage (partial vs full).
  - Concurrent application restrictions.
  - Saved student comparison sets.
- **Rule Constraints**: Rule 8 (Record ownership on saved comparison sets).
