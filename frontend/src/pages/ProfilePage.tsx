import React, { useState } from "react";
import {
  getStoredProfile,
  saveStoredProfile,
  INITIAL_STUDENT_PROFILE,
  MockStudentProfile,
} from "../mock/mockData";
import { StudyLevel } from "../types";
import { Card, Button, Input, Badge } from "../components/ui";
import {
  User,
  ShieldCheck,
  Save,
  RotateCcw,
  Plus,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

export const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<MockStudentProfile>(getStoredProfile());
  const [academicResults, setAcademicResults] = useState<[string, string][]>(
    Object.entries(profile.academic_results)
  );
  const [newSubject, setNewSubject] = useState("");
  const [newGrade, setNewGrade] = useState("A");
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleProfileChange = (field: keyof MockStudentProfile, value: any) => {
    setProfile((prev) => ({
      ...prev,
      [field]: value,
    }));
    setSaveSuccess(false);
  };

  const handleGradeChange = (index: number, newGradeVal: string) => {
    const updated = [...academicResults];
    updated[index][1] = newGradeVal;
    setAcademicResults(updated);
    setSaveSuccess(false);
  };

  const handleRemoveSubject = (index: number) => {
    const updated = academicResults.filter((_, i) => i !== index);
    setAcademicResults(updated);
    setSaveSuccess(false);
  };

  const handleAddSubject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSubject.trim()) return;
    setAcademicResults((prev) => [...prev, [newSubject.trim(), newGrade]]);
    setNewSubject("");
    setSaveSuccess(false);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Validation
    if (profile.cgpa < 0 || profile.cgpa > 4.0) {
      setValidationError("CGPA must be between 0.00 and 4.00.");
      return;
    }
    if (profile.household_income !== null && profile.household_income < 0) {
      setValidationError("Household income cannot be negative.");
      return;
    }

    const resultsObj: Record<string, string> = {};
    academicResults.forEach(([subj, grade]) => {
      resultsObj[subj] = grade;
    });

    const updatedProfile: MockStudentProfile = {
      ...profile,
      academic_results: resultsObj,
    };

    saveStoredProfile(updatedProfile);
    setProfile(updatedProfile);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 4000);
  };

  const handleReset = () => {
    if (window.confirm("Reset profile back to default demo student data?")) {
      saveStoredProfile(INITIAL_STUDENT_PROFILE);
      setProfile(INITIAL_STUDENT_PROFILE);
      setAcademicResults(Object.entries(INITIAL_STUDENT_PROFILE.academic_results));
      setSaveSuccess(false);
      setValidationError(null);
    }
  };

  return (
    <div className="page-profile">
      <div className="page-header-row">
        <div>
          <h2>Student Profile Configuration</h2>
          <p className="page-subtitle">
            Configure your academic and demographic profile for deterministic Rule 2 eligibility evaluations.
          </p>
        </div>
        <div className="page-header-actions">
          <Button variant="outline" onClick={handleReset} type="button">
            <RotateCcw size={14} style={{ marginRight: 6 }} /> Reset Demo Profile
          </Button>
        </div>
      </div>

      {/* What-If Workflow Advisory Callout */}
      <div className="info-callout">
        <Sparkles size={20} className="info-callout-icon" />
        <div>
          <strong>Persistent Profile vs What-If Simulator:</strong>
          <p>
            Changes saved here update your permanent profile records. If you only want to test hypothetical scenarios
            (e.g., <em>"What if my CGPA increases to 3.90?"</em>), visit any scholarship detail page and use the
            <strong> What-If Simulation tab</strong> without modifying this stored record.
          </p>
        </div>
      </div>

      {saveSuccess && (
        <div className="alert-banner success-banner">
          <CheckCircle2 size={18} />
          <span>Profile successfully updated in local memory store!</span>
        </div>
      )}

      {validationError && (
        <div className="alert-banner danger-banner">
          <AlertCircle size={18} />
          <span>{validationError}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="profile-form-grid">
        {/* Left Card: Academic & Identity Credentials */}
        <Card title="Personal & Academic Parameters" subtitle="Evaluated directly against scholarship criteria">
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <Input
              value={profile.full_name}
              onChange={(e) => handleProfileChange("full_name", e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <Input
              type="email"
              value={profile.email}
              onChange={(e) => handleProfileChange("email", e.target.value)}
              required
            />
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label className="form-label">Nationality / Citizenship</label>
              <select
                className="form-select"
                value={profile.nationality}
                onChange={(e) => {
                  handleProfileChange("nationality", e.target.value);
                  handleProfileChange("citizenship", e.target.value);
                }}
              >
                <option value="Malaysian">Malaysian (MyKad)</option>
                <option value="Non-Malaysian">International Student</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">State of Origin</label>
              <Input
                value={profile.state_of_origin}
                onChange={(e) => handleProfileChange("state_of_origin", e.target.value)}
              />
            </div>
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label className="form-label">Current Study Level</label>
              <select
                className="form-select"
                value={profile.study_level}
                onChange={(e) => handleProfileChange("study_level", e.target.value)}
              >
                <option value={StudyLevel.UNDERGRADUATE}>Undergraduate (Bachelor's Degree)</option>
                <option value={StudyLevel.POSTGRADUATE}>Postgraduate (Master's / PhD)</option>
                <option value={StudyLevel.PRE_UNIVERSITY}>Pre-University (Foundation / STPM / A-Levels)</option>
                <option value={StudyLevel.SECONDARY}>Secondary (SPM / O-Levels)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Current Undergraduate / Pre-U CGPA</label>
              <Input
                type="number"
                step="0.01"
                min="0.00"
                max="4.00"
                value={profile.cgpa}
                onChange={(e) => handleProfileChange("cgpa", parseFloat(e.target.value) || 0)}
                required
              />
              <span className="form-help">Scale 0.00 to 4.00</span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Field of Study</label>
            <Input
              value={profile.field_of_study}
              onChange={(e) => handleProfileChange("field_of_study", e.target.value)}
              placeholder="e.g. Computer Science, Mechanical Engineering"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Intended Future Field / Specialisation</label>
            <Input
              value={profile.intended_field}
              onChange={(e) => handleProfileChange("intended_field", e.target.value)}
              placeholder="e.g. Artificial Intelligence, Renewable Energy"
            />
          </div>
        </Card>

        {/* Right Column: Household Income & Academic Results */}
        <div className="profile-col-right">
          {/* Household Income (Rule 5 Compliant) */}
          <Card
            title="Household Income (Optional)"
            subtitle="Rule 5: Client-side privacy for need-based scholarship priority"
          >
            <div className="form-group">
              <label className="form-label">Monthly Gross Household Income (MYR)</label>
              <Input
                type="number"
                step="100"
                min="0"
                value={profile.household_income !== null ? profile.household_income : ""}
                onChange={(e) => {
                  const val = e.target.value === "" ? null : parseFloat(e.target.value);
                  handleProfileChange("household_income", val);
                }}
                placeholder="Optional (leave empty if undisclosed)"
              />
              <span className="form-help">
                E.g. RM 4,800. Used solely to match need-based thresholds (e.g. B40/M40 priority).
              </span>
            </div>

            <div className="rule-note">
              <ShieldCheck size={16} />
              <span>
                <strong>Rule 5 Privacy Guarantee:</strong> Household income is never shared with third parties or used for unapproved queries. Leaving this empty simply marks income requirements as "Unresolved".
              </span>
            </div>
          </Card>

          {/* Academic Results Breakdown Table */}
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
              {academicResults.map(([subj, grade], idx) => (
                <div key={idx} className="results-item-row">
                  <span className="subject-name">{subj}</span>
                  <select
                    className="grade-select"
                    value={grade}
                    onChange={(e) => handleGradeChange(idx, e.target.value)}
                  >
                    <option value="A+">A+</option>
                    <option value="A">A</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B">B</option>
                    <option value="C+">C+</option>
                    <option value="C">C</option>
                    <option value="D">D</option>
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
              ))}
            </div>

            {/* Add Subject Mini Form */}
            <div className="add-subject-row">
              <Input
                placeholder="Add subject (e.g. Additional Mathematics)"
                value={newSubject}
                onChange={(e) => setNewSubject(e.target.value)}
                style={{ flex: 1 }}
              />
              <select
                className="grade-select"
                value={newGrade}
                onChange={(e) => setNewGrade(e.target.value)}
              >
                <option value="A+">A+</option>
                <option value="A">A</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B">B</option>
                <option value="C+">C+</option>
                <option value="C">C</option>
              </select>
              <Button type="button" variant="secondary" size="sm" onClick={handleAddSubject}>
                <Plus size={14} style={{ marginRight: 4 }} /> Add
              </Button>
            </div>
          </Card>

          <div className="form-submit-row">
            <Button type="submit" size="lg">
              <Save size={16} style={{ marginRight: 6 }} /> Save Profile Updates
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};
