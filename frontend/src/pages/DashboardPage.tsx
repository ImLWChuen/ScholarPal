import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getStoredProfile,
  getStoredApplications,
  getStoredScholarships,
  getStoredInterviews,
  evaluateEligibility,
  MockStudentProfile,
  MockApplication,
  MockScholarship,
  MockInterview,
} from "../mock/mockData";
import { OverallEligibility, ApplicationStage } from "../types";
import { Card, Badge, Button } from "../components/ui";
import { ReadinessBar } from "../components/ReadinessBar";
import { StageBadge, OverallEligibilityBadge } from "../components/StatusBadges";
import {
  User,
  Search,
  KanbanSquare,
  Calendar,
  Scale,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Sparkles,
  ExternalLink,
} from "lucide-react";

export const DashboardPage: React.FC = () => {
  const [profile, setProfile] = useState<MockStudentProfile>(getStoredProfile());
  const [applications, setApplications] = useState<MockApplication[]>(getStoredApplications());
  const [scholarships, setScholarships] = useState<MockScholarship[]>(getStoredScholarships());
  const [interviews, setInterviews] = useState<MockInterview[]>(getStoredInterviews());

  useEffect(() => {
    setProfile(getStoredProfile());
    setApplications(getStoredApplications());
    setScholarships(getStoredScholarships());
    setInterviews(getStoredInterviews());
  }, []);

  // Normalizes offset-free timestamps to intended Malaysian Standard Time (UTC+8)
  const parseInterviewTimestamp = (ts: string): number => {
    if (!ts.includes("Z") && !/[+-]\d{2}:?\d{2}$/.test(ts)) {
      return new Date(`${ts}+08:00`).getTime();
    }
    return new Date(ts).getTime();
  };

  // Detect Interview Overlaps
  const detectOverlaps = () => {
    const conflicts: { item1: MockInterview; item2: MockInterview }[] = [];
    for (let i = 0; i < interviews.length; i++) {
      for (let j = i + 1; j < interviews.length; j++) {
        const int1 = interviews[i];
        const int2 = interviews[j];
        const start1 = parseInterviewTimestamp(int1.scheduled_at);
        const end1 = start1 + int1.duration_minutes * 60 * 1000;
        const start2 = parseInterviewTimestamp(int2.scheduled_at);
        const end2 = start2 + int2.duration_minutes * 60 * 1000;

        if (start1 < end2 && start2 < end1) {
          conflicts.push({ item1: int1, item2: int2 });
        }
      }
    }
    return conflicts;
  };

  const conflicts = detectOverlaps();

  // Calculate Eligibility Match Counts
  const eligibleMatches = scholarships.filter((s) => {
    const res = evaluateEligibility(s, profile);
    return res.overall === OverallEligibility.MEETS_RECORDED_REQUIREMENTS;
  }).length;

  return (
    <div className="page-dashboard">
      {/* Student Welcome & Overview Header */}
      <div className="dashboard-welcome-banner">
        <div>
          <h2>Selamat Datang, {profile.full_name} 👋</h2>
          <p className="dashboard-subtitle">
            ScholarPal student workspace & advisory hub. Track requirements, simulate eligibility, and prepare official submissions.
          </p>
        </div>
        <div className="profile-quick-stats">
          <div className="quick-stat">
            <span className="stat-label">Current CGPA</span>
            <span className="stat-value">{profile.cgpa.toFixed(2)}</span>
          </div>
          <div className="quick-stat">
            <span className="stat-label">Study Level</span>
            <span className="stat-value">{profile.study_level}</span>
          </div>
          <div className="quick-stat">
            <span className="stat-label">Household Income</span>
            <span className="stat-value">
              {profile.household_income !== null && profile.household_income !== undefined
                ? `RM ${profile.household_income.toLocaleString()}`
                : "Not Disclosed"}
            </span>
          </div>
          <Link to="/profile">
            <Button variant="outline" size="sm">
              <User size={14} style={{ marginRight: 6 }} /> Edit Profile
            </Button>
          </Link>
        </div>
      </div>

      {/* Critical Overlap Warning Alert */}
      {conflicts.length > 0 && (
        <div className="alert-banner warning-banner">
          <AlertTriangle className="alert-icon" size={24} />
          <div className="alert-content">
            <h4>⚠️ Critical Interview Scheduling Conflict Detected</h4>
            <p>
              You have {conflicts.length} overlapping interview session(s).{" "}
              <strong>{conflicts[0].item1.scholarship_title}</strong> conflicts with{" "}
              <strong>{conflicts[0].item2.scholarship_title}</strong> on{" "}
              {new Date(conflicts[0].item1.scheduled_at).toLocaleDateString("en-GB", {
                day: "numeric",
                month: "short",
                year: "numeric",
              })}.
            </p>
          </div>
          <Link to="/interviews">
            <Button variant="danger" size="sm">
              Resolve Conflict Now
            </Button>
          </Link>
        </div>
      )}

      {/* Student User Journey Stepper (Figure 11) */}
      <Card
        title="Student User Journey Flow"
        subtitle="Follow the recommended systematic progression to discover, evaluate, and track your scholarships"
        className="journey-card"
      >
        <div className="journey-stepper">
          <Link to="/profile" className="journey-step completed">
            <div className="step-num">1</div>
            <div className="step-info">
              <strong>Student Profile</strong>
              <span>Academic results & income</span>
            </div>
          </Link>
          <div className="journey-arrow">→</div>
          <Link to="/scholarships" className="journey-step active">
            <div className="step-num">2</div>
            <div className="step-info">
              <strong>Explore & Filter</strong>
              <span>Official sources & cycles</span>
            </div>
          </Link>
          <div className="journey-arrow">→</div>
          <Link to="/scholarships/sch-khazanah-global-2026" className="journey-step">
            <div className="step-num">3</div>
            <div className="step-info">
              <strong>Eligibility & What-If</strong>
              <span>Rule 2 deterministic logic</span>
            </div>
          </Link>
          <div className="journey-arrow">→</div>
          <Link to="/applications" className="journey-step">
            <div className="step-num">4</div>
            <div className="step-info">
              <strong>Track & Checklist</strong>
              <span>Readiness bar & stages</span>
            </div>
          </Link>
          <div className="journey-arrow">→</div>
          <Link to="/interviews" className="journey-step">
            <div className="step-num">5</div>
            <div className="step-info">
              <strong>Interviews</strong>
              <span>Conflict & overlap alerts</span>
            </div>
          </Link>
          <div className="journey-arrow">→</div>
          <Link to="/comparison" className="journey-step">
            <div className="step-num">6</div>
            <div className="step-info">
              <strong>Compare Options</strong>
              <span>Gap & bond obligations</span>
            </div>
          </Link>
        </div>
      </Card>

      {/* Metrics Grid */}
      <div className="stats-grid">
        <Card>
          <div className="metric-box">
            <div className="metric-icon bg-blue">
              <Search size={22} />
            </div>
            <div>
              <div className="metric-num">{scholarships.length}</div>
              <div className="metric-title">Monitored Scholarships</div>
              <span className="metric-subtitle">{eligibleMatches} match recorded criteria</span>
            </div>
          </div>
        </Card>

        <Card>
          <div className="metric-box">
            <div className="metric-icon bg-purple">
              <KanbanSquare size={22} />
            </div>
            <div>
              <div className="metric-num">{applications.length}</div>
              <div className="metric-title">Tracked Applications</div>
              <span className="metric-subtitle">
                Across {new Set(applications.map((a) => a.stage)).size} active stages
              </span>
            </div>
          </div>
        </Card>

        <Card>
          <div className="metric-box">
            <div className="metric-icon bg-amber">
              <Calendar size={22} />
            </div>
            <div>
              <div className="metric-num">{interviews.length}</div>
              <div className="metric-title">Scheduled Interviews</div>
              <span className="metric-subtitle">
                {conflicts.length > 0 ? (
                  <strong style={{ color: "var(--danger)" }}>1 Overlap Alert</strong>
                ) : (
                  "No timing conflicts"
                )}
              </span>
            </div>
          </div>
        </Card>

        <Card>
          <div className="metric-box">
            <div className="metric-icon bg-green">
              <Sparkles size={22} />
            </div>
            <div>
              <div className="metric-num">Rule 2</div>
              <div className="metric-title">Deterministic Engine</div>
              <span className="metric-subtitle">Predefined rules (never LLM)</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Dashboard Two-Column Section */}
      <div className="dashboard-columns">
        {/* Left Column: Active Applications & Document Readiness */}
        <div className="dashboard-col-left">
          <Card
            title="My Tracked Applications"
            subtitle="Monitor progress across stages and track required document readiness"
          >
            <div className="applications-preview-list">
              {applications.map((app) => {
                const scholarship = scholarships.find((s) => s.id === app.scholarship_id);
                const readyDocs = app.checklist.filter((d) => d.is_ready).length;
                const totalDocs = app.checklist.length;

                return (
                  <div key={app.id} className="app-preview-card">
                    <div className="app-preview-header">
                      <div>
                        <h4>{scholarship?.title || "Scholarship"}</h4>
                        <span className="text-muted text-sm">{scholarship?.provider} • Cycle: {scholarship?.application_cycle}</span>
                      </div>
                      <StageBadge stage={app.stage} />
                    </div>

                    <div className="app-preview-body">
                      <ReadinessBar readyCount={readyDocs} totalCount={totalDocs} />
                      {app.submission_reference && (
                        <div className="submission-ref-tag">
                          <span>Portal Ref: </span>
                          <code>{app.submission_reference}</code>
                        </div>
                      )}
                    </div>

                    <div className="app-preview-footer">
                      <Link to={`/scholarships/${app.scholarship_id}`} className="text-link text-sm">
                        View Criteria & What-If
                      </Link>
                      <Link to="/applications">
                        <Button variant="outline" size="sm">
                          Board View <ArrowRight size={14} style={{ marginLeft: 4 }} />
                        </Button>
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>

        {/* Right Column: Deadlines, Eligibility Highlights & Quick Actions */}
        <div className="dashboard-col-right">
          <Card title="Upcoming Official Deadlines" subtitle="Verified from official Malaysian scholarship portals">
            <div className="deadlines-list">
              {scholarships.map((sch) => {
                const evalResult = evaluateEligibility(sch, profile);
                return (
                  <div key={sch.id} className="deadline-item">
                    <div className="deadline-date-box">
                      <Clock size={16} />
                      <span>{new Date(sch.deadline).toLocaleDateString("en-GB", { day: "numeric", month: "short" })}</span>
                    </div>
                    <div className="deadline-details">
                      <h5>{sch.title}</h5>
                      <div className="deadline-meta">
                        <OverallEligibilityBadge status={evalResult.overall} />
                      </div>
                    </div>
                    <Link to={`/scholarships/${sch.id}`}>
                      <Button variant="outline" size="sm">
                        Inspect
                      </Button>
                    </Link>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card title="Quick Advisory Actions" subtitle="Fast paths for student tasks">
            <div className="quick-actions-list">
              <Link to="/scholarships" className="quick-action-btn">
                <Search size={18} />
                <div>
                  <strong>Search & Filter Scholarships</strong>
                  <span>Browse 2026 cycles with freshness timestamps</span>
                </div>
              </Link>
              <Link to="/interviews" className="quick-action-btn">
                <Calendar size={18} />
                <div>
                  <strong>Check Interview Schedule</strong>
                  <span>Verify venue/link and detect time collisions</span>
                </div>
              </Link>
              <Link to="/comparison" className="quick-action-btn">
                <Scale size={18} />
                <div>
                  <strong>Compare Up to 3 Options</strong>
                  <span>Analyze funding gaps and service bonds</span>
                </div>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
