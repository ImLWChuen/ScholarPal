import React from "react";
import { Link } from "react-router-dom";
import { useQueries, useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Calendar,
  KanbanSquare,
  Scale,
  Search,
  Sparkles,
  User,
} from "lucide-react";
import { ApiError } from "../api/client";
import {
  ApplicationChecklistDto,
  ApplicationDto,
  fetchApplicationChecklist,
  fetchApplications,
  fetchInterviews,
  InterviewDto,
} from "../api/dashboard";
import { fetchMyProfile, StudentProfileDto } from "../api/profile";
import { ReadinessBar } from "../components/ReadinessBar";
import { StageBadge } from "../components/StatusBadges";
import { Button, Card } from "../components/ui";
import { useAuth } from "../features/auth/AuthContext";
import { ApplicationStage } from "../types";

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  const profileQuery = useQuery<StudentProfileDto | null, ApiError>({
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

  const applicationsQuery = useQuery<ApplicationDto[], ApiError>({
    queryKey: ["applications"],
    queryFn: fetchApplications,
  });

  const interviewsQuery = useQuery<InterviewDto[], ApiError>({
    queryKey: ["interviews"],
    queryFn: fetchInterviews,
  });

  const applications = applicationsQuery.data ?? [];
  const interviews = interviewsQuery.data ?? [];
  const profile = profileQuery.data ?? null;

  const checklistQueries = useQueries({
    queries: applications.map((app) => ({
      queryKey: ["application-checklist", app.id],
      queryFn: () => fetchApplicationChecklist(app.id),
      enabled: applications.length > 0,
    })),
  });

  const checklistByAppId = new Map<string, ApplicationChecklistDto>();
  applications.forEach((app, idx) => {
    const res = checklistQueries[idx]?.data;
    if (res) {
      checklistByAppId.set(app.id, res);
    }
  });

  const isLoading =
    profileQuery.isLoading || applicationsQuery.isLoading || interviewsQuery.isLoading;
  const firstError = profileQuery.error || applicationsQuery.error || interviewsQuery.error;

  const parseInterviewTimestamp = (ts: string): number => {
    if (!ts.includes("Z") && !/[+-]\d{2}:?\d{2}$/.test(ts)) {
      return new Date(`${ts}+08:00`).getTime();
    }
    return new Date(ts).getTime();
  };

  const detectOverlaps = () => {
    const DEFAULT_DURATION_MS = 60 * 60 * 1000;
    const conflicts: { item1: InterviewDto; item2: InterviewDto }[] = [];
    for (let i = 0; i < interviews.length; i++) {
      for (let j = i + 1; j < interviews.length; j++) {
        const int1 = interviews[i];
        const int2 = interviews[j];
        const start1 = parseInterviewTimestamp(int1.scheduled_at);
        const end1 = start1 + DEFAULT_DURATION_MS;
        const start2 = parseInterviewTimestamp(int2.scheduled_at);
        const end2 = start2 + DEFAULT_DURATION_MS;

        if (start1 < end2 && start2 < end1) {
          conflicts.push({ item1: int1, item2: int2 });
        }
      }
    }
    return conflicts;
  };

  const conflicts = detectOverlaps();

  if (isLoading) {
    return (
      <div className="auth-loading-state" role="status" aria-live="polite">
        <div className="loading-spinner" />
        <p>Loading your ScholarPal dashboard...</p>
      </div>
    );
  }

  return (
    <div className="page-dashboard">
      {firstError && (
        <div className="alert-banner danger-banner" role="alert">
          <AlertCircle size={18} />
          <span>{firstError.message || "Failed to load dashboard data."}</span>
          <Button
            variant="outline"
            size="sm"
            type="button"
            onClick={() => {
              profileQuery.refetch();
              applicationsQuery.refetch();
              interviewsQuery.refetch();
            }}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Student Welcome & Overview Header */}
      <div className="dashboard-welcome-banner">
        <div>
          <h2>Selamat Datang, {user?.full_name || "Student"}</h2>
          <p className="dashboard-subtitle">
            ScholarPal student workspace & advisory hub. Track requirements, checklist readiness, and official submissions.
          </p>
        </div>
        <div className="profile-quick-stats">
          <div className="quick-stat">
            <span className="stat-label">Current CGPA</span>
            <span className="stat-value">
              {profile?.cgpa !== null && profile?.cgpa !== undefined
                ? profile.cgpa.toFixed(2)
                : "Not Set"}
            </span>
          </div>
          <div className="quick-stat">
            <span className="stat-label">Study Level</span>
            <span className="stat-value">{profile?.study_level || "Not Set"}</span>
          </div>
          <div className="quick-stat">
            <span className="stat-label">Household Income</span>
            <span className="stat-value">
              {profile?.household_income !== null && profile?.household_income !== undefined
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
            <h4>Interview Scheduling Conflict Detected</h4>
            <p>
              You have {conflicts.length} overlapping interview session(s):{" "}
              <strong>{conflicts[0].item1.round_name}</strong> conflicts with{" "}
              <strong>{conflicts[0].item2.round_name}</strong> on{" "}
              {new Date(conflicts[0].item1.scheduled_at).toLocaleDateString("en-GB", {
                day: "numeric",
                month: "short",
                year: "numeric",
              })}
              .
            </p>
          </div>
          <Link to="/interviews">
            <Button variant="danger" size="sm">
              Resolve Conflict
            </Button>
          </Link>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="stats-grid">
        <Card>
          <div className="metric-box">
            <div className="metric-icon bg-blue">
              <User size={22} />
            </div>
            <div>
              <div className="metric-num">{profile ? "Active" : "Incomplete"}</div>
              <div className="metric-title">Student Profile</div>
              <span className="metric-subtitle">
                {profile?.field_of_study || "Add your study details"}
              </span>
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
                  <strong style={{ color: "var(--danger)" }}>
                    {conflicts.length} Overlap Alert
                  </strong>
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
        <div className="dashboard-col-left">
          <Card
            title="My Tracked Applications"
            subtitle="Monitor progress across stages and track required document readiness"
          >
            {applications.length === 0 ? (
              <div className="empty-state-box">
                <p>You have no saved scholarship applications yet.</p>
                <Link to="/scholarships" style={{ marginTop: 8, display: "inline-block" }}>
                  <Button variant="outline" size="sm">
                    Browse Scholarships
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="applications-preview-list">
                {applications.map((app) => {
                  const checklistData = checklistByAppId.get(app.id);
                  const readyDocs = checklistData?.readiness.ready_count ?? 0;
                  const totalDocs = checklistData?.readiness.total_required ?? 0;

                  return (
                    <div key={app.id} className="app-preview-card">
                      <div className="app-preview-header">
                        <div>
                          <h4>Scholarship {app.scholarship_id}</h4>
                          <span className="text-muted text-sm">
                            Application ID: {app.id}
                          </span>
                        </div>
                        <StageBadge stage={app.stage as ApplicationStage} />
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
                          View Criteria
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
            )}
          </Card>
        </div>

        <div className="dashboard-col-right">
          <Card title="Upcoming Interviews" subtitle="Scheduled rounds from your saved applications">
            {interviews.length === 0 ? (
              <div className="empty-state-box">
                <p>No interviews scheduled yet.</p>
              </div>
            ) : (
              <div className="deadlines-list">
                {interviews.map((interview) => (
                  <div key={interview.id} className="deadline-item">
                    <div className="deadline-date-box">
                      <Calendar size={16} />
                      <span>
                        {new Date(interview.scheduled_at).toLocaleDateString("en-GB", {
                          day: "numeric",
                          month: "short",
                        })}
                      </span>
                    </div>
                    <div className="deadline-details">
                      <h5>{interview.round_name}</h5>
                      <span className="text-muted text-sm">
                        Status: {interview.status}
                        {interview.location_or_link ? ` • ${interview.location_or_link}` : ""}
                      </span>
                    </div>
                    <Link to="/interviews">
                      <Button variant="outline" size="sm">
                        Inspect
                      </Button>
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card title="Quick Advisory Actions" subtitle="Fast paths for student tasks">
            <div className="quick-actions-list">
              <Link to="/scholarships" className="quick-action-btn">
                <Search size={18} />
                <div>
                  <strong>Search & Filter Scholarships</strong>
                  <span>Browse cycles with freshness timestamps</span>
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
