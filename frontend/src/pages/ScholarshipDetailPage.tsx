import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  getStoredScholarship,
  getStoredProfile,
  saveStoredProfile,
  getStoredApplications,
  saveStoredApplications,
  evaluateEligibility,
  MockScholarship,
  MockStudentProfile,
  MockApplication,
} from "../mock/mockData";
import {
  ApplicationStage,
  OverallEligibility,
  RequirementOutcome,
  StudyLevel,
} from "../types";
import { Card, Button, Input, Badge } from "../components/ui";
import {
  FreshnessBadge,
  OverallEligibilityBadge,
  RequirementOutcomeBadge,
} from "../components/StatusBadges";
import { ReadinessBar } from "../components/ReadinessBar";
import {
  ExternalLink,
  Clock,
  Calendar,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  XCircle,
  FileText,
  ShieldAlert,
  ArrowLeft,
  RotateCcw,
  PlusCircle,
  Info,
} from "lucide-react";

export const ScholarshipDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [scholarship, setScholarship] = useState<MockScholarship | undefined>(undefined);
  const [profile, setProfile] = useState<MockStudentProfile>(getStoredProfile());
  const [activeTab, setActiveTab] = useState<"overview" | "eligibility" | "whatif" | "checklist">(
    "eligibility"
  );

  // What-If Simulator Temporary State (Figure 12 Workflow)
  const [simulatedCgpa, setSimulatedCgpa] = useState<number>(profile.cgpa);
  const [simulatedIncome, setSimulatedIncome] = useState<number | null>(profile.household_income);
  const [simulatedStudyLevel, setSimulatedStudyLevel] = useState<string>(profile.study_level);
  const [simulatedField, setSimulatedField] = useState<string>(profile.field_of_study);
  const [hasSimulated, setHasSimulated] = useState<boolean>(false);
  const [applySuccessNotice, setApplySuccessNotice] = useState<boolean>(false);

  // Application Tracking & Checklist State
  const [applications, setApplications] = useState<MockApplication[]>(getStoredApplications());

  useEffect(() => {
    if (id) {
      const found = getStoredScholarship(id);
      setScholarship(found);
    }
    const currentProfile = getStoredProfile();
    setProfile(currentProfile);
    setSimulatedCgpa(currentProfile.cgpa);
    setSimulatedIncome(currentProfile.household_income);
    setSimulatedStudyLevel(currentProfile.study_level);
    setSimulatedField(currentProfile.field_of_study);
  }, [id]);

  if (!scholarship) {
    return (
      <div className="not-found-container">
        <h3>Scholarship Not Found</h3>
        <p>The requested scholarship could not be found or has been archived.</p>
        <Link to="/scholarships">
          <Button variant="outline">
            <ArrowLeft size={16} style={{ marginRight: 6 }} /> Back to Scholarships
          </Button>
        </Link>
      </div>
    );
  }

  // Baseline evaluation with saved persistent profile
  const baselineEval = evaluateEligibility(scholarship, profile);

  // What-If simulated profile
  const simulatedProfile: MockStudentProfile = {
    ...profile,
    cgpa: simulatedCgpa,
    household_income: simulatedIncome,
    study_level: simulatedStudyLevel,
    field_of_study: simulatedField,
  };
  const simulatedEval = evaluateEligibility(scholarship, simulatedProfile);

  // Existing application check
  const existingApp = applications.find((a) => a.scholarship_id === scholarship.id);

  // Toggle checklist item readiness
  const handleToggleChecklist = (docId: string) => {
    if (!existingApp) {
      alert("Please track this application first before updating checklist readiness.");
      return;
    }
    const updatedApps = applications.map((app) => {
      if (app.id === existingApp.id) {
        const updatedChecklist = app.checklist.map((item) =>
          item.required_document_id === docId ? { ...item, is_ready: !item.is_ready } : item
        );
        return { ...app, checklist: updatedChecklist };
      }
      return app;
    });
    setApplications(updatedApps);
    saveStoredApplications(updatedApps);
  };

  // Add to tracked applications
  const handleStartTracking = () => {
    if (existingApp) {
      navigate("/applications");
      return;
    }

    const newApp: MockApplication = {
      id: `app-${Date.now()}`,
      scholarship_id: scholarship.id,
      student_id: profile.id,
      stage: ApplicationStage.SAVED,
      checklist: scholarship.required_documents.map((doc) => ({
        required_document_id: doc.id,
        name: doc.name,
        is_ready: false,
      })),
      tasks: [
        { id: `tsk-1-${Date.now()}`, title: "Review official guidelines PDF", is_completed: false },
        { id: `tsk-2-${Date.now()}`, title: "Gather certified documents", is_completed: false },
      ],
    };

    const updated = [...applications, newApp];
    setApplications(updated);
    saveStoredApplications(updated);
    setActiveTab("checklist");
  };

  // Apply What-If proposed values to persistent profile (Figure 12)
  const handleApplyWhatIfToPersistentProfile = () => {
    // Validate simulated inputs with the same profile rules as ProfilePage
    if (simulatedCgpa < 0 || simulatedCgpa > 4.0) {
      alert("Invalid What-If value: CGPA must be between 0.00 and 4.00.");
      return;
    }
    if (simulatedIncome !== null && simulatedIncome < 0) {
      alert("Invalid What-If value: Household income cannot be negative.");
      return;
    }
    if (!simulatedField.trim()) {
      alert("Invalid What-If value: Field of study cannot be empty.");
      return;
    }

    if (
      window.confirm(
        "Apply these proposed what-if values to your permanent profile? This will update your profile across ScholarPal."
      )
    ) {
      const newPersistentProfile: MockStudentProfile = {
        ...profile,
        cgpa: simulatedCgpa,
        household_income: simulatedIncome,
        study_level: simulatedStudyLevel,
        field_of_study: simulatedField.trim(),
      };
      saveStoredProfile(newPersistentProfile);
      setProfile(newPersistentProfile);
      setApplySuccessNotice(true);
      setTimeout(() => setApplySuccessNotice(false), 4000);
    }
  };

  const handleResetWhatIf = () => {
    setSimulatedCgpa(profile.cgpa);
    setSimulatedIncome(profile.household_income);
    setSimulatedStudyLevel(profile.study_level);
    setSimulatedField(profile.field_of_study);
    setHasSimulated(false);
  };

  // Document Readiness calculations
  const totalDocs = scholarship.required_documents.length;
  const readyDocs = existingApp
    ? existingApp.checklist.filter((c) => c.is_ready).length
    : 0;

  return (
    <div className="page-scholarship-detail">
      {/* Back button */}
      <div className="back-nav-bar">
        <Link to="/scholarships" className="back-link">
          <ArrowLeft size={16} /> Back to Scholarship Directory
        </Link>
      </div>

      {/* Main Header Card with Rule 7 disclaimer and Crawl Timestamps */}
      <div className="detail-header-card">
        <div className="detail-header-main">
          <div className="header-badges">
            <span className="provider-pill">{scholarship.provider}</span>
            <span className="cycle-pill">Cycle: {scholarship.application_cycle}</span>
            <FreshnessBadge status={scholarship.freshness} />
          </div>

          <h2 className="detail-title">{scholarship.title}</h2>

          <div className="detail-header-meta">
            <div className="meta-pill">
              <Clock size={14} />
              <span>Last checked: <strong>{scholarship.last_successful_check}</strong></span>
            </div>
            <div className="meta-pill">
              <Calendar size={14} />
              <span>Last human review: <strong>{scholarship.last_review_at}</strong></span>
            </div>
            <div className="meta-pill deadline">
              <span>Official Deadline: <strong>{new Date(scholarship.deadline).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}</strong></span>
            </div>
          </div>
        </div>

        <div className="header-actions-col">
          <a
            href={scholarship.official_portal_url}
            target="_blank"
            rel="noreferrer"
            className="btn-portal-official"
          >
            Visit Official Portal <ExternalLink size={16} style={{ marginLeft: 6 }} />
          </a>
          <div className="portal-rule-disclaimer">
            <ShieldAlert size={14} />
            <span>Rule 7: ScholarPal is an advisory tool. Official submissions must be submitted directly on the provider portal.</span>
          </div>

          {!existingApp ? (
            <Button onClick={handleStartTracking} size="sm">
              <PlusCircle size={14} style={{ marginRight: 6 }} /> Track Application
            </Button>
          ) : (
            <Link to="/applications">
              <Button variant="outline" size="sm">
                View on Application Board
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="detail-tabs-bar">
        <button
          className={`detail-tab ${activeTab === "eligibility" ? "active" : ""}`}
          onClick={() => setActiveTab("eligibility")}
        >
          <CheckCircle2 size={16} />
          <span>Eligibility Explanation Panel (Rule 2)</span>
        </button>

        <button
          className={`detail-tab ${activeTab === "whatif" ? "active" : ""}`}
          onClick={() => setActiveTab("whatif")}
        >
          <Sparkles size={16} />
          <span>What-If Simulation (Figure 12)</span>
        </button>

        <button
          className={`detail-tab ${activeTab === "checklist" ? "active" : ""}`}
          onClick={() => setActiveTab("checklist")}
        >
          <FileText size={16} />
          <span>Checklist & Readiness Bar</span>
        </button>

        <button
          className={`detail-tab ${activeTab === "overview" ? "active" : ""}`}
          onClick={() => setActiveTab("overview")}
        >
          <Info size={16} />
          <span>Overview & Financial Terms</span>
        </button>
      </div>

      {/* TAB CONTENT: ELIGIBILITY EXPLANATION PANEL (RULE 2) */}
      {activeTab === "eligibility" && (
        <div className="tab-pane-eligibility">
          <div className="overall-verdict-banner">
            <div className="verdict-banner-left">
              <span className="verdict-label">Deterministic Evaluation Result:</span>
              <OverallEligibilityBadge status={baselineEval.overall} />
            </div>
            <div className="verdict-banner-right">
              <span className="rule-compliance-tag">
                Complies with Non-Negotiable Rule 2 (No LLM hallucinations)
              </span>
            </div>
          </div>

          <Card
            title="Recorded Criteria Breakdown"
            subtitle="Each condition is evaluated strictly using predefined deterministic operators. Subjective criteria are flagged for provider review."
          >
            <div className="criteria-table">
              <div className="criteria-table-head">
                <span className="col-desc">Requirement Description</span>
                <span className="col-excerpt">Verbatim Source Excerpt</span>
                <span className="col-mandatory">Mandatory?</span>
                <span className="col-status">Outcome</span>
                <span className="col-reason">Deterministic Rationale</span>
              </div>

              {baselineEval.evaluations.map((item) => (
                <div key={item.requirement_id} className="criteria-table-row">
                  <div className="col-desc">
                    <strong>{item.description}</strong>
                  </div>
                  <div className="col-excerpt">
                    <blockquote>"{item.source_excerpt}"</blockquote>
                  </div>
                  <div className="col-mandatory">
                    {item.is_mandatory ? (
                      <Badge variant="danger">Mandatory</Badge>
                    ) : (
                      <Badge variant="neutral">Priority / Optional</Badge>
                    )}
                  </div>
                  <div className="col-status">
                    <RequirementOutcomeBadge outcome={item.outcome} />
                  </div>
                  <div className="col-reason">
                    <span className="reason-text">{item.reason}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="eligibility-legend">
              <div className="legend-item">
                <Badge variant="success">Satisfied</Badge>
                <span>Recorded profile attribute definitively satisfies the rule threshold.</span>
              </div>
              <div className="legend-item">
                <Badge variant="danger">Unmet</Badge>
                <span>Recorded profile attribute fails to meet the threshold.</span>
              </div>
              <div className="legend-item">
                <Badge variant="warning">Unresolved</Badge>
                <span>Missing student attribute or subjective criterion requiring manual provider discretion.</span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* TAB CONTENT: WHAT-IF FORM (FIGURE 12 WORKFLOW) */}
      {activeTab === "whatif" && (
        <div className="tab-pane-whatif">
          <div className="info-callout">
            <Sparkles size={20} className="info-callout-icon" />
            <div>
              <strong>Profile Change Reassessment & What-If Simulation:</strong>
              <p>
                Simulate hypothetical changes to your CGPA, income, or study level to see if your eligibility
                transitions from <em>Unmet / Needs Clarification</em> to <em>Meets Recorded Requirements</em>.
                Hypothetical changes remain isolated in this simulator unless you choose to confirm and update your saved profile.
              </p>
            </div>
          </div>

          {applySuccessNotice && (
            <div className="alert-banner success-banner">
              <CheckCircle2 size={18} />
              <span>Simulated values have been applied to your permanent student profile!</span>
            </div>
          )}

          <div className="whatif-comparison-grid">
            {/* Simulation Input Controls */}
            <Card title="Hypothetical Proposed Values" subtitle="Adjust inputs to simulate revised eligibility">
              <div className="form-group">
                <label className="form-label">Hypothetical CGPA</label>
                <Input
                  type="number"
                  step="0.01"
                  min="0.00"
                  max="4.00"
                  value={simulatedCgpa}
                  onChange={(e) => {
                    setSimulatedCgpa(parseFloat(e.target.value) || 0);
                    setHasSimulated(true);
                  }}
                />
                <span className="form-help">Current Profile: {profile.cgpa.toFixed(2)}</span>
              </div>

              <div className="form-group">
                <label className="form-label">Hypothetical Monthly Household Income (RM)</label>
                <Input
                  type="number"
                  step="100"
                  min="0"
                  value={simulatedIncome !== null ? simulatedIncome : ""}
                  onChange={(e) => {
                    setSimulatedIncome(e.target.value === "" ? null : parseFloat(e.target.value));
                    setHasSimulated(true);
                  }}
                />
                <span className="form-help">
                  Current Profile: {profile.household_income ? `RM ${profile.household_income.toLocaleString()}` : "Not Disclosed"}
                </span>
              </div>

              <div className="form-group">
                <label className="form-label">Study Level</label>
                <select
                  className="form-select"
                  value={simulatedStudyLevel}
                  onChange={(e) => {
                    setSimulatedStudyLevel(e.target.value);
                    setHasSimulated(true);
                  }}
                >
                  <option value={StudyLevel.UNDERGRADUATE}>Undergraduate</option>
                  <option value={StudyLevel.POSTGRADUATE}>Postgraduate</option>
                  <option value={StudyLevel.PRE_UNIVERSITY}>Pre-University (Foundation / STPM)</option>
                  <option value={StudyLevel.SECONDARY}>Secondary (SPM)</option>
                </select>
                <span className="form-help">Current Profile: {profile.study_level}</span>
              </div>

              <div className="form-group">
                <label className="form-label">Field of Study</label>
                <Input
                  value={simulatedField}
                  onChange={(e) => {
                    setSimulatedField(e.target.value);
                    setHasSimulated(true);
                  }}
                />
                <span className="form-help">Current Profile: {profile.field_of_study}</span>
              </div>

              <div className="simulation-actions">
                <Button variant="secondary" onClick={handleResetWhatIf} size="sm">
                  <RotateCcw size={14} style={{ marginRight: 4 }} /> Reset to Current Profile
                </Button>
                <Button
                  variant="primary"
                  onClick={handleApplyWhatIfToPersistentProfile}
                  size="sm"
                  disabled={!hasSimulated}
                >
                  Confirm & Apply to Saved Profile
                </Button>
              </div>
            </Card>

            {/* Live Eligibility Diff */}
            <Card
              title="Simulated Reassessment Diff"
              subtitle="Comparison between baseline saved profile and proposed what-if values"
            >
              <div className="diff-header-box">
                <div className="diff-box">
                  <span className="diff-title">Current Baseline:</span>
                  <OverallEligibilityBadge status={baselineEval.overall} />
                </div>
                <div className="diff-arrow">➔</div>
                <div className="diff-box">
                  <span className="diff-title">Simulated What-If:</span>
                  <OverallEligibilityBadge status={simulatedEval.overall} />
                </div>
              </div>

              <div className="criteria-diff-list">
                {simulatedEval.evaluations.map((simReq) => {
                  const baseReq = baselineEval.evaluations.find(
                    (b) => b.requirement_id === simReq.requirement_id
                  );
                  const changed = baseReq?.outcome !== simReq.outcome;

                  return (
                    <div
                      key={simReq.requirement_id}
                      className={`diff-item-row ${changed ? "diff-highlight" : ""}`}
                    >
                      <div className="diff-item-left">
                        <strong>{simReq.description}</strong>
                        <p className="diff-item-reason">{simReq.reason}</p>
                      </div>
                      <div className="diff-item-right">
                        {changed ? (
                          <div className="diff-badge-transition">
                            <span className="old-state">{baseReq?.outcome}</span>
                            <span>➔</span>
                            <RequirementOutcomeBadge outcome={simReq.outcome} />
                          </div>
                        ) : (
                          <RequirementOutcomeBadge outcome={simReq.outcome} />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* TAB CONTENT: CHECKLIST AND READINESS BAR */}
      {activeTab === "checklist" && (
        <div className="tab-pane-checklist">
          {/* Readiness Bar Card */}
          <Card title="Document Readiness Evaluation" subtitle="Section 5.4 Readiness Metric Calculation">
            <ReadinessBar readyCount={readyDocs} totalCount={totalDocs} showCounts={true} />

            <div className="formula-explanation">
              <code>Document Readiness = (Known Ready Documents / Total Known Required Documents) * 100%</code>
              <p>
                If no documents are specified by the provider, readiness displays <strong>"Not Available"</strong> rather than an assumed 100%.
              </p>
            </div>
          </Card>

          {/* Interactive Document Checklist Items */}
          <Card
            title="Required Documents Checklist"
            subtitle="Mark documents as verified and ready for official provider submission"
          >
            {!existingApp ? (
              <div className="checklist-empty-prompt">
                <p>You have not yet tracked this scholarship in your applications.</p>
                <Button onClick={handleStartTracking}>
                  <PlusCircle size={16} style={{ marginRight: 6 }} /> Start Tracking This Scholarship
                </Button>
              </div>
            ) : (
              <div className="checklist-items-table">
                {existingApp.checklist.map((item) => {
                  const docDef = scholarship.required_documents.find(
                    (d) => d.id === item.required_document_id
                  );

                  return (
                    <div key={item.required_document_id} className="checklist-row">
                      <div className="checklist-checkbox-col">
                        <input
                          type="checkbox"
                          id={`chk-${item.required_document_id}`}
                          checked={item.is_ready}
                          onChange={() => handleToggleChecklist(item.required_document_id)}
                          className="checklist-checkbox"
                        />
                      </div>
                      <div className="checklist-info-col">
                        <label
                          htmlFor={`chk-${item.required_document_id}`}
                          className={`doc-title ${item.is_ready ? "ready-text" : ""}`}
                        >
                          {item.name}
                        </label>
                        {docDef?.format_instructions && (
                          <span className="doc-instructions">
                            Instructions: {docDef.format_instructions}
                          </span>
                        )}
                      </div>
                      <div className="checklist-status-col">
                        {item.is_ready ? (
                          <Badge variant="success">Ready ✓</Badge>
                        ) : (
                          <Badge variant="warning">Pending Upload / Verification</Badge>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>
      )}

      {/* TAB CONTENT: OVERVIEW & FINANCIAL TERMS */}
      {activeTab === "overview" && (
        <div className="tab-pane-overview">
          <div className="overview-grid">
            <Card title="Financial Coverage & Allowances" subtitle="Sponsorship package terms">
              <div className="spec-item">
                <span className="spec-label">Tuition Fees:</span>
                <span className="spec-val">
                  {scholarship.tuition_covered ? (
                    <Badge variant="success">100% Fully Covered</Badge>
                  ) : (
                    "Partial"
                  )}
                </span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Monthly Living Allowance:</span>
                <span className="spec-val">RM {scholarship.monthly_allowance.toLocaleString()} / month</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Coverage Summary:</span>
                <span className="spec-val">{scholarship.coverage_summary}</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Estimated Annual Cost:</span>
                <span className="spec-val">RM {scholarship.estimated_annual_cost.toLocaleString()}</span>
              </div>
            </Card>

            <Card title="Obligations & Governance" subtitle="Post-graduation service bonds and academic conditions">
              <div className="spec-item">
                <span className="spec-label">Service Bond Duration:</span>
                <span className="spec-val">
                  {scholarship.bond_duration_years > 0 ? (
                    <strong>{scholarship.bond_duration_years} Years Obligation</strong>
                  ) : (
                    <Badge variant="success">Bond-Free</Badge>
                  )}
                </span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Service Obligation Details:</span>
                <span className="spec-val">{scholarship.service_obligation_notes}</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Renewal Conditions:</span>
                <span className="spec-val">{scholarship.renewal_conditions}</span>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};
