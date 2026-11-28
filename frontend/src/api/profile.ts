import { apiClient } from "./client";

export interface StudentProfileDto {
  id: string;
  user_id: string;
  study_level: string | null;
  education_level: string | null;
  nationality: string | null;
  citizenship: string | null;
  state_of_origin: string | null;
  field_of_study: string | null;
  intended_field: string | null;
  academic_results: Record<string, string | number> | null;
  household_income: number | null;
  cgpa: number | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface StudentProfileUpdateDto {
  study_level?: string | null;
  education_level?: string | null;
  nationality?: string | null;
  citizenship?: string | null;
  state_of_origin?: string | null;
  field_of_study?: string | null;
  intended_field?: string | null;
  academic_results?: Record<string, string | number> | null;
  household_income?: number | null;
  cgpa?: number | null;
}

export async function fetchMyProfile(): Promise<StudentProfileDto> {
  return apiClient<StudentProfileDto>("/api/v1/profiles/me");
}

export async function createMyProfile(
  data: StudentProfileUpdateDto
): Promise<StudentProfileDto> {
  return apiClient<StudentProfileDto>("/api/v1/profiles", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateMyProfile(
  data: StudentProfileUpdateDto
): Promise<StudentProfileDto> {
  return apiClient<StudentProfileDto>("/api/v1/profiles/me", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}
