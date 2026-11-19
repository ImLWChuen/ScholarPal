/**
 * Mock data store for ScholarPal React wireframes.
 * All data strictly adheres to generated shared schemas and enums.
 * Supports in-memory and localStorage updates for interactive wireframe testing.
 */

import {
  ApplicationStage,
  EvidenceLabel,
  FreshnessStatus,
  OverallEligibility,
  RequirementOutcome,
  ScholarshipStatus,
  StudyLevel,
  VersionStatus,
} from "../types";

export interface MockRequirement {
  id: string;
  type: string;
  operator: string;
  value: any;
  is_mandatory: boolean;
  source_excerpt: string;
  description: string;
}

export interface MockRequiredDocument {
  id: string;
  name: string;
  is_mandatory: boolean;
  format_instructions?: string;
  is_ready?: boolean;
}

export interface MockScholarship {
  id: string;
  title: string;
  provider: string;
  official_portal_url: string;
  application_cycle: string;
  status: ScholarshipStatus;
  freshness: FreshnessStatus;
  last_successful_check: string;
  last_review_at: string;
  deadline: string;
  study_level: StudyLevel;
  field_of_study: string;
  coverage_summary: string;
  tuition_covered: boolean;
  monthly_allowance: number;
  bond_duration_years: number;
  estimated_annual_cost: number;
  service_obligation_notes: string;
  renewal_conditions: string;
  requirements: MockRequirement[];
  required_documents: MockRequiredDocument[];
}

export interface MockStudentProfile {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  study_level: string;
  nationality: string;
  citizenship: string;
  state_of_origin: string;
  field_of_study: string;
  intended_field: string;
  cgpa: number;
  household_income: number | null; // Rule 5: Nullable
  academic_results: Record<string, string>;
}

export interface MockApplication {
  id: string;
  scholarship_id: string;
  student_id: string;
  stage: ApplicationStage;
  submitted_at?: string | null;
  submission_reference?: string | null;
  notes?: string;
  checklist: {
    required_document_id: string;
    name: string;
    is_ready: boolean;
    file_name?: string;
    uploaded_at?: string;
    notes?: string;
  }[];
  tasks: {
    id: string;
    title: string;
    is_completed: boolean;
    due_date?: string;
  }[];
}

export interface MockInterview {
  id: string;
  application_id: string;
  scholarship_title: string;
  round_name: string;
  scheduled_at: string; // ISO string
  duration_minutes: number;
  location_or_link: string;
  status: string;
  prep_notes: string;
}

export interface MockAdminReviewItem {
  id: string;
  scholarship_title: string;
  provider: string;
  source_url: string;
  application_cycle: string;
  extracted_criteria: {
    name: string;
    rule: string;
    source_excerpt: string;
  }[];
  jev_verdict: EvidenceLabel;
  jev_confidence: number;
  jev_probabilities: Record<string, number>;
  review_status: VersionStatus;
  created_at: string;
}

// ---------------------------------------------------------------------------
// INITIAL MOCK DATA
// ---------------------------------------------------------------------------

export const INITIAL_STUDENT_PROFILE: MockStudentProfile = {
  id: "prof-demo-1",
  user_id: "usr-demo-1",
  full_name: "Ahmad bin Zulkifli",
  email: "ahmad.student@scholarpal.my",
  study_level: StudyLevel.UNDERGRADUATE,
  nationality: "Malaysian",
  citizenship: "Malaysian",
  state_of_origin: "Penang",
  field_of_study: "Computer Science",
  intended_field: "Artificial Intelligence & Data Engineering",
  cgpa: 3.85,
  household_income: 4800.0, // M40 income bracket in MYR
  academic_results: {
    "Bahasa Melayu": "A+",
    "English": "A",
    "Mathematics": "A+",
    "Additional Mathematics": "A",
    "Physics": "A+",
    "Chemistry": "A",
    "Computer Science": "A+",
  },
};

export const INITIAL_SCHOLARSHIPS: MockScholarship[] = [
  {
    id: "sch-khazanah-global-2026",
    title: "Yayasan Khazanah Global Scholarship 2026",
    provider: "Yayasan Khazanah",
    official_portal_url: "https://www.yayasankhazanah.com.my/scholarships",
    application_cycle: "2026 Cycle A",
    status: ScholarshipStatus.OPEN,
    freshness: FreshnessStatus.FRESH,
    last_successful_check: "2026-11-19 14:30 MYT",
    last_review_at: "2026-11-18 10:15 MYT",
    deadline: "2026-12-15T23:59:59Z",
    study_level: StudyLevel.UNDERGRADUATE,
    field_of_study: "Computer Science, Economics, Engineering, Mathematics",
    coverage_summary: "Full Tuition + RM 4,500/mo living allowance, return airfare & laptops",
    tuition_covered: true,
    monthly_allowance: 4500.0,
    bond_duration_years: 5,
    estimated_annual_cost: 60000.0,
    service_obligation_notes: "5 years service bond with Khazanah Nasional or designated GLCs upon graduation.",
    renewal_conditions: "Maintain minimum CGPA 3.50 each academic semester.",
    requirements: [
      {
        id: "req-khz-1",
        type: "academic_cgpa",
        operator: "gte",
        value: 3.75,
        is_mandatory: true,
        source_excerpt: "Possess strong academic credentials with minimum CGPA of 3.75 or equivalent.",
        description: "Minimum undergraduate CGPA of 3.75",
      },
      {
        id: "req-khz-2",
        type: "nationality",
        operator: "eq",
        value: "Malaysian",
        is_mandatory: true,
        source_excerpt: "Applicants must be Malaysian citizens holding a valid MyKad.",
        description: "Must be a Malaysian citizen",
      },
      {
        id: "req-khz-3",
        type: "study_level",
        operator: "in",
        value: ["Undergraduate", "Postgraduate"],
        is_mandatory: true,
        source_excerpt: "Offered to students pursuing full-time Undergraduate or Postgraduate studies.",
        description: "Full-time Undergraduate or Postgraduate studies",
      },
      {
        id: "req-khz-4",
        type: "household_income_max",
        operator: "lte",
        value: 12000.0,
        is_mandatory: false,
        source_excerpt: "Priority is accorded to applicants from households with monthly gross income under RM 12,000.",
        description: "Household income under RM 12,000 (Priority flag)",
      },
      {
        id: "req-khz-5",
        type: "leadership_assessment",
        operator: "eq",
        value: true,
        is_mandatory: false,
        source_excerpt: "Demonstrated extracurricular leadership in secondary or university co-curricular bodies.",
        description: "Demonstrated co-curricular and leadership potential",
      },
    ],
    required_documents: [
      {
        id: "doc-khz-1",
        name: "Certified SPM / A-Levels Result Slip",
        is_mandatory: true,
        format_instructions: "PDF format, verified by school principal or commissioner of oaths",
      },
      {
        id: "doc-khz-2",
        name: "Official Academic Transcript (Latest Semester)",
        is_mandatory: true,
        format_instructions: "Official university transcript with university seal",
      },
      {
        id: "doc-khz-3",
        name: "Confidential Academic Recommendation Letter",
        is_mandatory: true,
        format_instructions: "Written by faculty dean or academic mentor on institutional letterhead",
      },
    ],
  },
  {
    id: "sch-petronas-pesp-2026",
    title: "Yayasan PETRONAS Education Sponsorship Programme (PESP) 2026",
    provider: "Yayasan PETRONAS",
    official_portal_url: "https://www.yayasanpetronas.com.my/pesp-programme",
    application_cycle: "2026 Intake",
    status: ScholarshipStatus.OPEN,
    freshness: FreshnessStatus.FRESH,
    last_successful_check: "2026-11-19 12:00 MYT",
    last_review_at: "2026-11-17 11:30 MYT",
    deadline: "2026-12-05T23:59:59Z",
    study_level: StudyLevel.UNDERGRADUATE,
    field_of_study: "Chemical Engineering, Computer Science, Geosciences, Data Analytics",
    coverage_summary: "Full academic tuition fees + RM 3,500/mo allowance + books & onboarding grant",
    tuition_covered: true,
    monthly_allowance: 3500.0,
    bond_duration_years: 5,
    estimated_annual_cost: 50000.0,
    service_obligation_notes: "5 years employment bond with PETRONAS or its group of companies.",
    renewal_conditions: "Minimum semester GPA 3.30 throughout the course of study.",
    requirements: [
      {
        id: "req-pet-1",
        type: "academic_cgpa",
        operator: "gte",
        value: 3.5,
        is_mandatory: true,
        source_excerpt: "Minimum current CGPA 3.50 or minimum 8A's in SPM examination.",
        description: "Minimum CGPA 3.50 or 8A's in SPM",
      },
      {
        id: "req-pet-2",
        type: "nationality",
        operator: "eq",
        value: "Malaysian",
        is_mandatory: true,
        source_excerpt: "Open exclusively to Malaysian citizens aged between 17 and 23 years.",
        description: "Malaysian citizen aged 17–23",
      },
      {
        id: "req-pet-3",
        type: "stem_field",
        operator: "in",
        value: ["Engineering", "Computer Science", "Information Technology", "Geology"],
        is_mandatory: true,
        source_excerpt: "Study discipline must fall within accredited STEM and energy transition courses.",
        description: "Accredited STEM discipline",
      },
    ],
    required_documents: [
      {
        id: "doc-pet-1",
        name: "SPM Official Result Slip",
        is_mandatory: true,
      },
      {
        id: "doc-pet-2",
        name: "Parent/Guardian Income Tax Form (BE / EA Form)",
        is_mandatory: true,
        format_instructions: "Latest year LHDN tax submission receipt",
      },
      {
        id: "doc-pet-3",
        name: "Co-curricular Leadership Certificates",
        is_mandatory: true,
      },
    ],
  },
  {
    id: "sch-jpa-pidn-2026",
    title: "JPA Program Ijazah Dalam Negara (PIDN) 2026",
    provider: "Jabatan Perkhidmatan Awam (JPA)",
    official_portal_url: "https://esilav2.jpa.gov.my",
    application_cycle: "2026 Fasa 1",
    status: ScholarshipStatus.OPEN,
    freshness: FreshnessStatus.UNCERTAIN, // Flagged freshness to demonstrate Rule 4!
    last_successful_check: "2026-11-18 08:00 MYT (Previous cycle check)",
    last_review_at: "2026-11-10 16:00 MYT",
    deadline: "2026-11-30T17:00:00Z",
    study_level: StudyLevel.UNDERGRADUATE,
    field_of_study: "All accredited undergraduate degree courses in IPTA",
    coverage_summary: "Subsidized tuition fees + RM 1,200/mo living allowance + thesis grant",
    tuition_covered: true,
    monthly_allowance: 1200.0,
    bond_duration_years: 7,
    estimated_annual_cost: 25000.0,
    service_obligation_notes: "Federal government convertible loan: serve government agency for 7 years.",
    renewal_conditions: "Active enrollment with satisfactory pass standing in public university.",
    requirements: [
      {
        id: "req-jpa-1",
        type: "academic_cgpa",
        operator: "gte",
        value: 3.5,
        is_mandatory: true,
        source_excerpt: "Mendapat sekurang-kurangnya PNGK 3.50 pada semester pertama pengajian universiti awam.",
        description: "Minimum undergraduate CGPA 3.50 in public university",
      },
      {
        id: "req-jpa-2",
        type: "nationality",
        operator: "eq",
        value: "Malaysian",
        is_mandatory: true,
        source_excerpt: "Warganegara Malaysia dan belum mencapai umur 25 tahun.",
        description: "Malaysian citizen under 25 years old",
      },
      {
        id: "req-jpa-3",
        type: "university_type",
        operator: "eq",
        value: "IPTA",
        is_mandatory: true,
        source_excerpt: "Sedang mengikuti pengajian di Universiti Awam (IPTA) tempatan yang diiktiraf MQA.",
        description: "Currently enrolled in local Public University (IPTA)",
      },
    ],
    required_documents: [
      {
        id: "doc-jpa-1",
        name: "Surat Tawaran Kemasukan Universiti Awam",
        is_mandatory: true,
      },
      {
        id: "doc-jpa-2",
        name: "Slip Pengesahan PNGK Peperiksaan Semester Lepas",
        is_mandatory: true,
      },
    ],
  },
  {
    id: "sch-bnm-kijang-2026",
    title: "Bank Negara Malaysia Kijang Scholarship 2026",
    provider: "Bank Negara Malaysia",
    official_portal_url: "https://www.bnm.gov.my/careers/scholarships",
    application_cycle: "2026 Pre-U / Undergraduate",
    status: ScholarshipStatus.UPCOMING,
    freshness: FreshnessStatus.FRESH,
    last_successful_check: "2026-11-19 15:00 MYT",
    last_review_at: "2026-11-18 14:00 MYT",
    deadline: "2027-01-15T23:59:59Z",
    study_level: StudyLevel.PRE_UNIVERSITY,
    field_of_study: "Economics, Accounting, Finance, Actuarial Science, Data Science",
    coverage_summary: "Full overseas & local sponsorship including allowance of RM 5,000/mo and book allowance",
    tuition_covered: true,
    monthly_allowance: 5000.0,
    bond_duration_years: 6,
    estimated_annual_cost: 65000.0,
    service_obligation_notes: "6 years employment bond at Bank Negara Malaysia upon graduation.",
    renewal_conditions: "Excellence standing and participation in BNM vacation training programs.",
    requirements: [
      {
        id: "req-bnm-1",
        type: "academic_spm",
        operator: "gte",
        value: 8,
        is_mandatory: true,
        source_excerpt: "Minimum 8A's (A/A+) in SPM examination or equivalent international benchmark.",
        description: "Minimum 8A's in SPM",
      },
      {
        id: "req-bnm-2",
        type: "nationality",
        operator: "eq",
        value: "Malaysian",
        is_mandatory: true,
        source_excerpt: "Open strictly to Malaysian citizens with leadership involvement.",
        description: "Malaysian citizenship",
      },
    ],
    required_documents: [
      {
        id: "doc-bnm-1",
        name: "SPM Certificate and Detailed Statement",
        is_mandatory: true,
      },
      {
        id: "doc-bnm-2",
        name: "National Co-Curricular Assessment Report",
        is_mandatory: true,
      },
      {
        id: "doc-bnm-3",
        name: "Personal Essay: Monetary Policy & Digital Economy",
        is_mandatory: true,
      },
    ],
  },
];

export const INITIAL_APPLICATIONS: MockApplication[] = [
  {
    id: "app-1",
    scholarship_id: "sch-khazanah-global-2026",
    student_id: "usr-demo-1",
    stage: ApplicationStage.PREPARING,
    submission_reference: null,
    notes: "Targeting Overseas UK Computer Science track. Draft personal statement completed.",
    checklist: [
      {
        required_document_id: "doc-khz-1",
        name: "Certified SPM / A-Levels Result Slip",
        is_ready: true,
        file_name: "Ahmad_SPM_Certified_2025.pdf",
        uploaded_at: "2026-11-15 11:20 MYT",
        notes: "Certified at Penang High Court",
      },
      {
        required_document_id: "doc-khz-2",
        name: "Official Academic Transcript (Latest Semester)",
        is_ready: true,
        file_name: "Transcript_Sem2_USM_Verified.pdf",
        uploaded_at: "2026-11-16 16:45 MYT",
        notes: "Contains Dean's List stamp",
      },
      {
        required_document_id: "doc-khz-3",
        name: "Confidential Academic Recommendation Letter",
        is_ready: false, // 2 out of 3 ready -> readiness bar = 66%
        notes: "Requested from Assoc. Prof. Dr. Ramona; expected by Nov 28",
      },
    ],
    tasks: [
      {
        id: "tsk-1",
        title: "Follow up with Prof Ramona regarding recommendation letter",
        is_completed: false,
        due_date: "2026-11-26",
      },
      {
        id: "tsk-2",
        title: "Draft 500-word leadership essay on AI ethics",
        is_completed: true,
        due_date: "2026-11-20",
      },
    ],
  },
  {
    id: "app-2",
    scholarship_id: "sch-petronas-pesp-2026",
    student_id: "usr-demo-1",
    stage: ApplicationStage.SUBMITTED,
    submitted_at: "2026-11-17 14:22:00 MYT",
    submission_reference: "PESP-2026-882194",
    notes: "Submitted on official PETRONAS Education portal. Awaiting shortlisting outcome.",
    checklist: [
      {
        required_document_id: "doc-pet-1",
        name: "SPM Official Result Slip",
        is_ready: true,
        file_name: "SPM_Slip_Official.pdf",
      },
      {
        required_document_id: "doc-pet-2",
        name: "Parent/Guardian Income Tax Form (BE / EA Form)",
        is_ready: true,
        file_name: "Parent_Tax_Assessment_2025.pdf",
      },
      {
        required_document_id: "doc-pet-3",
        name: "Co-curricular Leadership Certificates",
        is_ready: true,
        file_name: "National_Coding_Cert_1st.pdf",
      },
    ],
    tasks: [],
  },
  {
    id: "app-3",
    scholarship_id: "sch-jpa-pidn-2026",
    student_id: "usr-demo-1",
    stage: ApplicationStage.INTERVIEW,
    submitted_at: "2026-11-05 09:10:00 MYT",
    submission_reference: "JPA-PIDN-2026-9041",
    notes: "Invited to virtual selection board interview on 25 November 2026.",
    checklist: [
      {
        required_document_id: "doc-jpa-1",
        name: "Surat Tawaran Kemasukan Universiti Awam",
        is_ready: true,
        file_name: "USM_Tawaran_Ijazah.pdf",
      },
      {
        required_document_id: "doc-jpa-2",
        name: "Slip Pengesahan PNGK Peperiksaan Semester Lepas",
        is_ready: true,
        file_name: "Slip_Peperiksaan_Sem1.pdf",
      },
    ],
    tasks: [
      {
        id: "tsk-jpa-1",
        title: "Review Malaysia Madani core principles & Public Service ethos",
        is_completed: false,
        due_date: "2026-11-24",
      },
    ],
  },
  {
    id: "app-4",
    scholarship_id: "sch-bnm-kijang-2026",
    student_id: "usr-demo-1",
    stage: ApplicationStage.SAVED,
    notes: "Saved to explore when applications open in January 2027.",
    checklist: [],
    tasks: [],
  },
];

export const INITIAL_INTERVIEWS: MockInterview[] = [
  {
    id: "int-1",
    application_id: "app-1",
    scholarship_title: "Yayasan Khazanah Global Scholarship 2026",
    round_name: "Virtual Leadership Assessment & Panel Interview",
    scheduled_at: "2026-11-25T10:00:00",
    duration_minutes: 90, // 10:00 AM - 11:30 AM
    location_or_link: "https://zoom.us/j/9812498129 (Passcode: KHZ2026)",
    status: "Confirmed",
    prep_notes: "Prepare case study on sovereign wealth investment and AI governance.",
  },
  {
    id: "int-2",
    application_id: "app-3",
    scholarship_title: "JPA Program Ijazah Dalam Negara (PIDN) 2026",
    round_name: "JPA State Selection Board Interview",
    scheduled_at: "2026-11-25T11:00:00", // 11:00 AM - 12:00 PM -> OVERLAPS with int-1 (10:00 - 11:30)!
    duration_minutes: 60,
    location_or_link: "Bilik Temuduga 4, Kompleks C, Putrajaya / Webex JPA",
    status: "Confirmed",
    prep_notes: "Bring physical copies of original NRIC, SPM certificate, and Dean's award.",
  },
];

export const INITIAL_ADMIN_REVIEWS: MockAdminReviewItem[] = [
  {
    id: "rev-shell-2026",
    scholarship_title: "Shell Malaysia STEM Scholarship 2026",
    provider: "Shell Malaysia",
    source_url: "https://www.shell.com.my/careers/students-and-graduates/scholarships.html",
    application_cycle: "2026 Cycle 1",
    extracted_criteria: [
      {
        name: "Academic Requirement",
        rule: "Minimum CGPA 3.60 in first-year Engineering or Geoscience",
        source_excerpt: "Candidates must have completed their first year of study with minimum CGPA 3.60.",
      },
      {
        name: "Nationality",
        rule: "Malaysian Citizen only",
        source_excerpt: "Open exclusively to Malaysian citizens with full-time enrollment.",
      },
    ],
    jev_verdict: EvidenceLabel.SUPPORTED,
    jev_confidence: 0.94,
    jev_probabilities: {
      supported: 0.94,
      contradicted: 0.04,
      unclear: 0.02,
    },
    review_status: VersionStatus.PENDING,
    created_at: "2026-11-19 09:12 MYT",
  },
  {
    id: "rev-gamuda-2026",
    scholarship_title: "Yayasan Gamuda Engineering & ESG Scholarship 2026",
    provider: "Yayasan Gamuda",
    source_url: "https://gamuda.com.my/sustainability-esg/yayasan-gamuda/scholarship/",
    application_cycle: "2026",
    extracted_criteria: [
      {
        name: "Academic Standing",
        rule: "Strong academic track record; no specific cutoff stated",
        source_excerpt: "Open to students with a proven record of academic brilliance and community engagement.",
      },
      {
        name: "Household Income Priority",
        rule: "B40 and M40 priority",
        source_excerpt: "Special consideration will be extended to deserving candidates from lower-income backgrounds.",
      },
    ],
    jev_verdict: EvidenceLabel.UNCLEAR,
    jev_confidence: 0.61,
    jev_probabilities: {
      supported: 0.28,
      contradicted: 0.11,
      unclear: 0.61,
    },
    review_status: VersionStatus.PENDING,
    created_at: "2026-11-19 11:45 MYT",
  },
];

// ---------------------------------------------------------------------------
// LOCAL STORAGE PERSISTENCE HELPERS
// ---------------------------------------------------------------------------

const STORAGE_KEYS = {
  PROFILE: "scholarpal_wireframe_profile",
  SCHOLARSHIPS: "scholarpal_wireframe_scholarships",
  APPLICATIONS: "scholarpal_wireframe_applications",
  INTERVIEWS: "scholarpal_wireframe_interviews",
  ADMIN_REVIEWS: "scholarpal_wireframe_admin_reviews",
  COMPARISON_IDS: "scholarpal_wireframe_comparison_ids",
};

export function getStoredProfile(): MockStudentProfile {
  const data = localStorage.getItem(STORAGE_KEYS.PROFILE);
  return data ? JSON.parse(data) : INITIAL_STUDENT_PROFILE;
}

export function saveStoredProfile(profile: MockStudentProfile): void {
  localStorage.setItem(STORAGE_KEYS.PROFILE, JSON.stringify(profile));
}

export function getStoredScholarships(): MockScholarship[] {
  const data = localStorage.getItem(STORAGE_KEYS.SCHOLARSHIPS);
  return data ? JSON.parse(data) : INITIAL_SCHOLARSHIPS;
}

export function getStoredScholarship(id: string): MockScholarship | undefined {
  const list = getStoredScholarships();
  return list.find((s) => s.id === id);
}

export function getStoredApplications(): MockApplication[] {
  const data = localStorage.getItem(STORAGE_KEYS.APPLICATIONS);
  return data ? JSON.parse(data) : INITIAL_APPLICATIONS;
}

export function saveStoredApplications(apps: MockApplication[]): void {
  localStorage.setItem(STORAGE_KEYS.APPLICATIONS, JSON.stringify(apps));
}

export function getStoredInterviews(): MockInterview[] {
  const data = localStorage.getItem(STORAGE_KEYS.INTERVIEWS);
  return data ? JSON.parse(data) : INITIAL_INTERVIEWS;
}

export function saveStoredInterviews(interviews: MockInterview[]): void {
  localStorage.setItem(STORAGE_KEYS.INTERVIEWS, JSON.stringify(interviews));
}

export function getStoredAdminReviews(): MockAdminReviewItem[] {
  const data = localStorage.getItem(STORAGE_KEYS.ADMIN_REVIEWS);
  return data ? JSON.parse(data) : INITIAL_ADMIN_REVIEWS;
}

export function saveStoredAdminReviews(reviews: MockAdminReviewItem[]): void {
  localStorage.setItem(STORAGE_KEYS.ADMIN_REVIEWS, JSON.stringify(reviews));
}

export function getStoredComparisonIds(): string[] {
  const data = localStorage.getItem(STORAGE_KEYS.COMPARISON_IDS);
  return data ? JSON.parse(data) : ["sch-khazanah-global-2026", "sch-petronas-pesp-2026"];
}

export function saveStoredComparisonIds(ids: string[]): void {
  localStorage.setItem(STORAGE_KEYS.COMPARISON_IDS, JSON.stringify(ids.slice(0, 3)));
}

// ---------------------------------------------------------------------------
// DETERMINISTIC ELIGIBILITY EVALUATOR (RULE 2)
// ---------------------------------------------------------------------------

export interface RequirementEvaluationResult {
  requirement_id: string;
  description: string;
  source_excerpt: string;
  is_mandatory: boolean;
  outcome: RequirementOutcome;
  reason: string;
}

export interface OverallEligibilityEvaluation {
  scholarship_id: string;
  overall: OverallEligibility;
  evaluations: RequirementEvaluationResult[];
}

export function evaluateEligibility(
  scholarship: MockScholarship,
  profile: MockStudentProfile
): OverallEligibilityEvaluation {
  const evaluations: RequirementEvaluationResult[] = [];
  let hasMandatoryUnmet = false;
  let hasUnresolved = false;

  for (const req of scholarship.requirements) {
    let outcome = RequirementOutcome.UNRESOLVED;
    let reason = "Criterion could not be definitively matched against recorded profile.";

    if (req.type === "academic_cgpa") {
      if (profile.cgpa == null) {
        outcome = RequirementOutcome.UNRESOLVED;
        reason = "Student CGPA not recorded in profile.";
      } else if (profile.cgpa >= req.value) {
        outcome = RequirementOutcome.SATISFIED;
        reason = `Student CGPA (${profile.cgpa.toFixed(2)}) meets or exceeds required ${req.value.toFixed(2)}.`;
      } else {
        outcome = RequirementOutcome.UNMET;
        reason = `Student CGPA (${profile.cgpa.toFixed(2)}) is below required ${req.value.toFixed(2)}.`;
      }
    } else if (req.type === "nationality") {
      if (!profile.nationality) {
        outcome = RequirementOutcome.UNRESOLVED;
        reason = "Student nationality not specified.";
      } else if (profile.nationality.toLowerCase() === String(req.value).toLowerCase()) {
        outcome = RequirementOutcome.SATISFIED;
        reason = `Student citizenship (${profile.nationality}) satisfies requirement.`;
      } else {
        outcome = RequirementOutcome.UNMET;
        reason = `Student citizenship (${profile.nationality}) does not match required ${req.value}.`;
      }
    } else if (req.type === "study_level") {
      if (!profile.study_level) {
        outcome = RequirementOutcome.UNRESOLVED;
        reason = "Study level not specified in profile.";
      } else if (Array.isArray(req.value) ? req.value.includes(profile.study_level) : profile.study_level === req.value) {
        outcome = RequirementOutcome.SATISFIED;
        reason = `Study level (${profile.study_level}) is eligible for this scholarship.`;
      } else {
        outcome = RequirementOutcome.UNMET;
        reason = `Current level (${profile.study_level}) does not match allowed levels.`;
      }
    } else if (req.type === "household_income_max") {
      if (profile.household_income == null) {
        outcome = RequirementOutcome.UNRESOLVED;
        reason = "Household income not recorded in profile.";
      } else if (profile.household_income <= req.value) {
        outcome = RequirementOutcome.SATISFIED;
        reason = `Household income (RM ${profile.household_income.toLocaleString()}) is within priority ceiling (RM ${req.value.toLocaleString()}).`;
      } else {
        outcome = RequirementOutcome.UNMET;
        reason = `Household income (RM ${profile.household_income.toLocaleString()}) exceeds target threshold.`;
      }
    } else if (req.type === "stem_field") {
      if (!profile.field_of_study) {
        outcome = RequirementOutcome.UNRESOLVED;
        reason = "Field of study not recorded in profile.";
      } else if (req.value.some((f: string) => profile.field_of_study.toLowerCase().includes(f.toLowerCase()))) {
        outcome = RequirementOutcome.SATISFIED;
        reason = `Field (${profile.field_of_study}) matches target STEM disciplines.`;
      } else {
        outcome = RequirementOutcome.UNMET;
        reason = `Field (${profile.field_of_study}) is not within listed disciplines.`;
      }
    } else {
      // Subjective criteria (e.g. leadership) - Rule 2: Subjective criteria never auto-verified
      outcome = RequirementOutcome.UNRESOLVED;
      reason = "Subjective / interview criteria requires provider assessment; cannot be auto-verified.";
    }

    if (req.is_mandatory && outcome === RequirementOutcome.UNMET) {
      hasMandatoryUnmet = true;
    }
    if (outcome === RequirementOutcome.UNRESOLVED) {
      hasUnresolved = true;
    }

    evaluations.push({
      requirement_id: req.id,
      description: req.description,
      source_excerpt: req.source_excerpt,
      is_mandatory: req.is_mandatory,
      outcome,
      reason,
    });
  }

  // Deterministic Overall Synthesis (Rule 2)
  let overall = OverallEligibility.MEETS_RECORDED_REQUIREMENTS;
  if (hasMandatoryUnmet) {
    overall = OverallEligibility.DOES_NOT_MEET_RECORDED_REQUIREMENTS;
  } else if (hasUnresolved) {
    overall = OverallEligibility.NEEDS_CLARIFICATION;
  }

  return {
    scholarship_id: scholarship.id,
    overall,
    evaluations,
  };
}

export function resetAllMockData(): void {
  Object.values(STORAGE_KEYS).forEach((k) => localStorage.removeItem(k));
}

