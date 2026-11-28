import { apiClient } from "./client";

export interface ApplicationDto {
  id: string;
  student_id: string;
  scholarship_id: string;
  stage: string;
  submitted_at: string | null;
  submission_reference: string | null;
  portal_submission_reference: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChecklistItemDto {
  id: string;
  application_id: string;
  required_document_id: string;
  file_path: string | null;
  file_name: string | null;
  is_ready: boolean;
  notes: string | null;
  uploaded_at: string | null;
  created_at: string;
}

export interface DocumentReadinessDto {
  ready_count: number;
  total_required: number | null;
  readiness_percentage: number | null;
  status: "not_available" | "not_started" | "partial" | "complete";
  display: string;
}

export interface ApplicationChecklistDto {
  application_id: string;
  readiness: DocumentReadinessDto;
  items: ChecklistItemDto[];
}

export interface InterviewDto {
  id: string;
  application_id: string;
  scheduled_at: string;
  location_or_link: string | null;
  round_name: string;
  status: string;
  feedback: string | null;
  created_at: string;
}

export async function fetchApplications(): Promise<ApplicationDto[]> {
  return apiClient<ApplicationDto[]>("/api/v1/applications");
}

export async function fetchApplicationChecklist(
  applicationId: string
): Promise<ApplicationChecklistDto> {
  return apiClient<ApplicationChecklistDto>(
    `/api/v1/applications/${encodeURIComponent(applicationId)}/checklist`
  );
}

export async function fetchInterviews(): Promise<InterviewDto[]> {
  return apiClient<InterviewDto[]>("/api/v1/interviews");
}
