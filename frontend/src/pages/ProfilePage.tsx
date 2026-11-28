import React, { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  Plus,
  RefreshCw,
  Save,
  ShieldCheck,
  Sparkles,
  Trash2,
} from "lucide-react";
import { ApiError } from "../api/client";
import {
  createMyProfile,
  fetchMyProfile,
  StudentProfileDto,
  StudentProfileUpdateDto,
  updateMyProfile,
} from "../api/profile";
import { Button, Card, Input } from "../components/ui";
import { useAuth } from "../features/auth/AuthContext";
import { StudyLevel } from "../types";

const VALID_GRADES = [
  "A+",
  "A",
  "A-",
  "B+",
  "B",
  "B-",
  "C+",
  "C",
  "C-",
  "D+",
  "D",
  "E",
  "F",
  "G",
  "O",
  "U",
  "PASS",
  "MERIT",
  "DISTINCTION",
];

function flattenAcademicResults(
  raw: Record<string, unknown> | null | undefined
): [string, string][] {
  if (!raw) return [];
  const entries: [string, string][] = [];
  for (const [key, val] of Object.entries(raw)) {
    if (val && typeof val === "object" && !Array.isArray(val)) {
      for (const [subKey, subVal] of Object.entries(val as Record<string, unknown>)) {
        if (subVal !== null && subVal !== undefined) {
          entries.push([subKey, String(subVal)]);
        }
      }
    } else if (val !== null && val !== undefined) {
      entries.push([key, String(val)]);
    }
  }
  return entries;
}

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const {
    data: profileData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<StudentProfileDto | null, ApiError>({
    queryKey: ["my-profile"],
    queryFn: async () => {
      try {
        return await fetchMyProfile();
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          return null;
        }
        throw err;
      }
    },
  });

  const [studyLevel, setStudyLevel] = useState<string>(StudyLevel.UNDERGRADUATE);
  const [nationality, setNationality] = useState<string>("Malaysian");
  const [stateOfOrigin, setStateOfOrigin] = useState<string>("");
  const [fieldOfStudy, setFieldOfStudy] = useState<string>("");
  const [intendedField, setIntendedField] = useState<string>("");
  const [cgpaDraft, setCgpaDraft] = useState<string>("");
  const [incomeDraft, setIncomeDraft] = useState<string>("");
  const [academicResults, setAcademicResults] = useState<[string, string][]>([]);
  const [newSubject, setNewSubject] = useState("");
  const [newGrade, setNewGrade] = useState("A");
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const syncFormFromProfile = (p: StudentProfileDto | null | undefined) => {
    setStudyLevel(p?.study_level || StudyLevel.UNDERGRADUATE);
    setNationality(p?.nationality || p?.citizenship || "Malaysian");
    setStateOfOrigin(p?.state_of_origin || "");
    setFieldOfStudy(p?.field_of_study || "");
    setIntendedField(p?.intended_field || "");
    setCgpaDraft(p?.cgpa !== null && p?.cgpa !== undefined ? p.cgpa.toString() : "");
    setIncomeDraft(
      p?.household_income !== null && p?.household_income !== undefined
        ? p.household_income.toString()
        : ""
    );
    setAcademicResults(flattenAcademicResults(p?.academic_results));
  };

  useEffect(() => {
    if (profileData !== undefined) {
      syncFormFromProfile(profileData);
    }
  }, [profileData]);

  const saveMutation = useMutation<StudentProfileDto, ApiError, StudentProfileUpdateDto>({
    mutationFn: async (payload) => {
      if (profileData === null) {
        return createMyProfile(payload);
      }
      return updateMyProfile(payload);
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["my-profile"], updated);
      setSaveSuccess(true);
      setValidationError(null);
      setTimeout(() => setSaveSuccess(false), 4000);
    },
    onError: (err) => {
      setValidationError(err.message || "Failed to save profile.");
      setSaveSuccess(false);
    },
  });

  const handleGradeChange = (index: number, newGradeVal: string) => {
    const updated = [...academicResults];
    updated[index] = [updated[index][0], newGradeVal];
    setAcademicResults(updated);
    setSaveSuccess(false);
  };

  const handleRemoveSubject = (index: number) => {
    setAcademicResults((prev) => prev.filter((_, i) => i !== index));
    setSaveSuccess(false);
  };

  const handleAddSubject = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = newSubject.trim();
    if (!trimmed) return;

    const existingIndex = academicResults.findIndex(
      ([subj]) => subj.toLowerCase() === trimmed.toLowerCase()
    );

    if (existingIndex >= 0) {
      const updated = [...academicResults];
      updated[existingIndex] = [updated[existingIndex][0], newGrade];
      setAcademicResults(updated);
    } else {
      setAcademicResults((prev) => [...prev, [trimmed, newGrade]]);
    }
    setNewSubject("");
    setSaveSuccess(false);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    setSaveSuccess(false);

    let parsedCgpa: number | null = null;
    if (cgpaDraft.trim() !== "") {
      parsedCgpa = Number(cgpaDraft);
      if (Number.isNaN(parsedCgpa) || parsedCgpa < 0 || parsedCgpa > 4.0) {
        setValidationError("CGPA must be a valid number between 0.00 and 4.00.");
        return;
      }
      parsedCgpa = Math.round(parsedCgpa * 100) / 100;
    }

    let parsedIncome: number | null = null;
    if (incomeDraft.trim() !== "") {
      parsedIncome = Number(incomeDraft);
      if (Number.isNaN(parsedIncome) || parsedIncome < 0) {
        setValidationError("Household income cannot be negative.");
        return;
      }
      parsedIncome = Math.round(parsedIncome * 100) / 100;
    }

    if (nationality.trim().length > 100) {
      setValidationError("Nationality must be at most 100 characters.");
      return;
    }
    if (stateOfOrigin.trim().length > 100) {
      setValidationError("State of origin must be at most 100 characters.");
      return;
    }
    if (fieldOfStudy.trim().length > 200) {
      setValidationError("Field of study must be at most 200 characters.");
      return;
    }
    if (intendedField.trim().length > 200) {
      setValidationError("Intended field must be at most 200 characters.");
      return;
    }

    const resultsObj: Record<string, string> = {};
    for (const [subj, grade] of academicResults) {
      const normalizedGrade = grade.trim().toUpperCase();
      if (!VALID_GRADES.includes(normalizedGrade)) {
        setValidationError(`Invalid grade '${grade}' for subject '${subj}'.`);
        return;
      }
      resultsObj[subj] = normalizedGrade;
    }

    const payload: StudentProfileUpdateDto = {
      study_level: studyLevel || null,
      nationality: nationality.trim() || null,
      citizenship: nationality.trim() || null,
      state_of_origin: stateOfOrigin.trim() || null,
      field_of_study: fieldOfStudy.trim() || null,
      intended_field: intendedField.trim() || null,
      cgpa: parsedCgpa,
      household_income: parsedIncome,
      academic_results: Object.keys(resultsObj).length > 0 ? resultsObj : null,
    };

    saveMutation.mutate(payload);
  };

  if (isLoading) {
    return (
      <div className="auth-loading-state" role="status" aria-live="polite">
        <div className="loading-spinner" />
        <p>Loading your student profile...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="page-profile">
        <div className="alert-banner danger-banner" role="alert">
          <AlertCircle size={18} />
          <span>{error?.message || "Unable to load profile from the server."}</span>
          <Button variant="outline" size="sm" onClick={() => refetch()} type="button">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-profile">
      <div className="page-header-row">
        <div>
          <h2>Student Profile Configuration</h2>
          <p className="page-subtitle">
            Configure your reusable academic and demographic profile. All changes are validated and audit-logged.
          </p>
        </div>
        <div className="page-header-actions">
          <Button
            variant="outline"
            onClick={() => syncFormFromProfile(profileData)}
            type="button"
            disabled={saveMutation.isPending}
          >
            <RefreshCw size={14} style={{ marginRight: 6 }} /> Revert Unsaved Changes
          </Button>
        </div>
      </div>

      <div className="info-callout">
        <Sparkles size={20} className="info-callout-icon" />
        <div>
          <strong>Persistent Profile vs What-If Simulator:</strong>
          <p>
            Changes saved here update your permanent profile records on the server and record an audit log entry.
          </p>
        </div>
      </div>

      {saveSuccess && (
        <div className="alert-banner success-banner" role="status">
          <CheckCircle2 size={18} />
          <span>Profile saved and audit-logged successfully!</span>
        </div>
      )}

      {validationError && (
        <div className="alert-banner danger-banner" role="alert">
          <AlertCircle size={18} />
          <span>{validationError}</span>
        </div>
      )}

      <form onSubmit={handleSave} noValidate className="profile-form-grid">
        {/* Left Card: Academic & Identity Credentials */}
        <Card title="Personal & Academic Parameters" subtitle="Evaluated against scholarship criteria">
          <div className="form-group">
            <label htmlFor="profile-full-name" className="form-label">
              Full Name
            </label>
            <Input id="profile-full-name" value={user?.full_name || ""} disabled readOnly />
          </div>

          <div className="form-group">
            <label htmlFor="profile-email" className="form-label">
              Email Address
            </label>
            <Input id="profile-email" type="email" value={user?.email || ""} disabled readOnly />
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label htmlFor="profile-nationality" className="form-label">
                Nationality / Citizenship
              </label>
              <select
                id="profile-nationality"
                className="form-select"
                value={nationality}
                onChange={(e) => {
                  setNationality(e.target.value);
                  setSaveSuccess(false);
                }}
              >
                <option value="Malaysian">Malaysian (MyKad)</option>
                <option value="Non-Malaysian">International Student</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="profile-state" className="form-label">
                State of Origin
              </label>
              <Input
                id="profile-state"
                value={stateOfOrigin}
                onChange={(e) => {
                  setStateOfOrigin(e.target.value);
                  setSaveSuccess(false);
                }}
                placeholder="e.g. Selangor, Penang"
                maxLength={100}
              />
            </div>
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label htmlFor="profile-study-level" className="form-label">
                Current Study Level
              </label>
              <select
                id="profile-study-level"
                className="form-select"
                value={studyLevel}
                onChange={(e) => {
                  setStudyLevel(e.target.value);
                  setSaveSuccess(false);
                }}
              >
                <option value={StudyLevel.UNDERGRADUATE}>Undergraduate (Bachelor's Degree)</option>
                <option value={StudyLevel.POSTGRADUATE}>Postgraduate (Master's / PhD)</option>
                <option value={StudyLevel.PRE_UNIVERSITY}>
                  Pre-University (Foundation / STPM / A-Levels)
                </option>
                <option value={StudyLevel.SECONDARY}>Secondary (SPM / O-Levels)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="profile-cgpa" className="form-label">
                Current CGPA (Optional)
              </label>
              <Input
                id="profile-cgpa"
                type="number"
                step="0.01"
                min="0.00"
                max="4.00"
                value={cgpaDraft}
                onChange={(e) => {
                  setCgpaDraft(e.target.value);
                  setSaveSuccess(false);
                }}
                placeholder="Leave empty if unknown"
              />
              <span className="form-help">Scale 0.00 to 4.00</span>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="profile-field" className="form-label">
              Field of Study
            </label>
            <Input
              id="profile-field"
              value={fieldOfStudy}
              onChange={(e) => {
                setFieldOfStudy(e.target.value);
                setSaveSuccess(false);
              }}
              placeholder="e.g. Computer Science, Mechanical Engineering"
              maxLength={200}
            />
          </div>

          <div className="form-group">
            <label htmlFor="profile-intended-field" className="form-label">
              Intended Future Field / Specialisation
            </label>
            <Input
              id="profile-intended-field"
              value={intendedField}
              onChange={(e) => {
                setIntendedField(e.target.value);
                setSaveSuccess(false);
              }}
              placeholder="e.g. Artificial Intelligence, Renewable Energy"
              maxLength={200}
            />
          </div>
        </Card>

        {/* Right Column: Household Income & Academic Results */}
        <div className="profile-col-right">
          <Card
            title="Household Income (Optional)"
            subtitle="Rule 5: Unknown values stay unknown (null), never zero"
          >
            <div className="form-group">
              <label htmlFor="profile-income" className="form-label">
                Monthly Gross Household Income (MYR)
              </label>
              <Input
                id="profile-income"
                type="number"
                step="any"
                min="0"
                value={incomeDraft}
                onChange={(e) => {
                  setIncomeDraft(e.target.value);
                  setSaveSuccess(false);
                }}
                placeholder="Optional (leave empty if undisclosed)"
              />
              <span className="form-help">
                E.g. RM 4,800. Used solely to match need-based thresholds.
              </span>
            </div>

            <div className="rule-note">
              <ShieldCheck size={16} />
              <span>
                <strong>Rule 5 Privacy Guarantee:</strong> Leaving this empty preserves it as unknown on the server instead of defaulting to zero.
              </span>
            </div>
          </Card>

          <Card
            title="Academic Results / Subject Grades"
            subtitle="Detailed examination records for subject-specific eligibility criteria"
          >
            <div className="academic-results-table">
              <div className="results-header-row">
                <span>Subject Name</span>
                <span>Grade Obtained</span>
                <span>Action</span>
              </div>
              {academicResults.length === 0 ? (
                <div className="empty-state-box">No subject grades recorded yet.</div>
              ) : (
                academicResults.map(([subj, grade], idx) => (
                  <div key={`${subj}-${idx}`} className="results-item-row">
                    <span className="subject-name">{subj}</span>
                    <select
                      className="grade-select"
                      value={grade}
                      onChange={(e) => handleGradeChange(idx, e.target.value)}
                    >
                      {VALID_GRADES.map((g) => (
                        <option key={g} value={g}>
                          {g}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      className="btn-icon danger"
                      onClick={() => handleRemoveSubject(idx)}
                      title="Remove subject"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="add-subject-row">
              <Input
                id="profile-new-subject"
                placeholder="Add subject (e.g. Additional Mathematics)"
                aria-label="Add subject name"
                value={newSubject}
                onChange={(e) => setNewSubject(e.target.value)}
                style={{ flex: 1 }}
              />
              <select
                className="grade-select"
                value={newGrade}
                onChange={(e) => setNewGrade(e.target.value)}
              >
                {VALID_GRADES.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
              <Button type="button" variant="secondary" size="sm" onClick={handleAddSubject}>
                <Plus size={14} style={{ marginRight: 4 }} /> Add
              </Button>
            </div>
          </Card>

          <div className="form-submit-row">
            <Button type="submit" size="lg" disabled={saveMutation.isPending}>
              <Save size={16} style={{ marginRight: 6 }} />
              {saveMutation.isPending ? "Saving..." : "Save Profile Updates"}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};
