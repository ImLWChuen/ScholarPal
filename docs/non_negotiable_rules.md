# ScholarPal Non-Negotiable Rules

The following eight architectural rules are strictly enforced across ScholarPal. No code or architecture changes may violate them:

---

### Rule 1: Deterministic Eligibility Engine
> **"Eligibility results come only from predefined rules, never from an LLM."**
- LLMs are strictly used for data extraction and parsing from raw source material.
- Every eligibility assessment is calculated deterministically via registered, auditable rule predicates (e.g., minimum CGPA, household income thresholds, Malaysian state quotas, course field matching).

---

### Rule 2: Three-State Requirement Evaluation
> **"Each requirement is satisfied, unmet or unresolved; overall result is Does not meet recorded requirements (any mandatory unmet), Needs clarification (none unmet but something missing or unclear), or Meets recorded requirements (all mandatory satisfied)."**
- Per-criterion states:
  - `satisfied`: Student definitely meets the condition.
  - `unmet`: Student definitely violates a mandatory condition.
  - `unresolved`: Student profile is missing information or provider condition requires human clarification.
- Overall calculation logic:
  - If **ANY** mandatory requirement is `unmet` $\rightarrow$ `Does not meet recorded requirements`.
  - Else if **NO** mandatory requirements are `unmet`, but at least one requirement is `unresolved` $\rightarrow$ `Needs clarification`.
  - Else if **ALL** mandatory requirements are `satisfied` $\rightarrow$ `Meets recorded requirements`.

---

### Rule 3: Jev Verification Assisting Admin (Never Auto-Publish)
> **"Jev results assist the administrator and never auto-publish."**
- Jev by TypeSafe AI evaluates extracted claims against source text using the `Choice` primitive.
- The outcome (`supported`, `contradicted`, `insufficient_evidence`) is surfaced directly to the administrator inside the Admin Review Console.
- A human administrator must explicitly approve or edit the record before it becomes publicly visible to students.

---

### Rule 4: Preserving Records on Retrieval Failure
> **"Failed retrieval keeps the last known record and flags uncertain freshness; it never marks a scholarship closed."**
- If a provider portal returns an HTTP 5xx/4xx error, times out, or changes layout, the existing scholarship record is preserved.
- Its freshness status is updated to `uncertain`, triggering an alert for administrative verification.
- A scholarship is marked `closed` **only** when the official portal explicitly indicates closure or deadline expiration.

---

### Rule 5: Data Integrity for Unknown Values
> **"Unknown values stay unknown, never zero."**
- Missing household income, CGPA, or test scores must remain `None` / `null`.
- Unknown values must never be coerced to `0` or default fallback values, preventing false-positive or false-negative eligibility evaluations.

---

### Rule 6: Ephemeral What-If Simulations
> **"What-if checks never modify saved data."**
- Students can simulate eligibility outcomes (e.g., "What if my CGPA improves to 3.8?" or "What if household income changes?").
- Simulations run against an in-memory profile overlay and must never mutate the student's persistent profile in PostgreSQL.

---

### Rule 7: External Portal Submissions
> **"Students submit on official provider portals; ScholarPal never marks submission automatically."**
- ScholarPal provides tracking checklists, deadline reminders, and direct links to provider portals.
- A scholarship application status is transitioned to `submitted_by_student` **only** when the student explicitly marks it as submitted.

---

### Rule 8: Strict Record Ownership
> **"Backend enforces record ownership on every student endpoint."**
- All student-specific endpoints (applications, profile updates, saved comparisons, what-if queries) authenticate the student token and strictly enforce that `resource.student_id == current_user.id`.
- Unauthorised access attempts return HTTP 403 Forbidden.
