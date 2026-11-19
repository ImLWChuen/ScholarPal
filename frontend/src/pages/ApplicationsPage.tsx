import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getStoredApplications,
  saveStoredApplications,
  getStoredScholarships,
  MockApplication,
  MockScholarship,
} from "../mock/mockData";
import { ApplicationStage } from "../types";
import { Card, Button, Badge } from "../components/ui";
import { ReadinessBar } from "../components/ReadinessBar";
import { StageBadge } from "../components/StatusBadges";
import {
  KanbanSquare,
  ShieldAlert,
  ArrowRight,
  ArrowLeft,
  ExternalLink,
  Plus,
  FileCheck2,
  Calendar,
} from "lucide-react";

export const ApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<MockApplication[]>(getStoredApplications());
  const [scholarships] = useState<MockScholarship[]>(getStoredScholarships());

  useEffect(() => {
    setApplications(getStoredApplications());
  }, []);

  const STAGES: ApplicationStage[] = [
    ApplicationStage.SAVED,
    ApplicationStage.PREPARING,
    ApplicationStage.SUBMITTED,
    ApplicationStage.INTERVIEW,
    ApplicationStage.OFFERED,
    ApplicationStage.UNSUCCESSFUL,
    ApplicationStage.WITHDRAWN,
  ];

  const handleMoveStage = (appId: string, newStage: ApplicationStage) => {
    const updated = applications.map((app) => {
      if (app.id === appId) {
        return {
          ...app,
          stage: newStage,
          submitted_at:
            newStage === ApplicationStage.SUBMITTED && !app.submitted_at
              ? new Date().toISOString()
              : app.submitted_at,
        };
      }
      return app;
    });
    setApplications(updated);
    saveStoredApplications(updated);
  };

  return (
    <div className="page-applications">
      <div className="page-header-row">
        <div>
          <h2>Application Lifecycle Board</h2>
          <p className="page-subtitle">
            Manage your scholarship application milestones across the 7 lifecycle stages.
          </p>
        </div>
        <div>
          <Link to="/scholarships">
            <Button size="sm">
              <Plus size={14} style={{ marginRight: 6 }} /> Track Another Scholarship
            </Button>
          </Link>
        </div>
      </div>

      {/* Official Portal Submission Boundary Banner (Rule 7) */}
      <div className="alert-banner info-banner">
        <ShieldAlert size={20} className="alert-icon" />
        <div className="alert-content">
          <strong>Official Portal Submission Boundary (Rule 7 Compliance):</strong>
          <p>
            ScholarPal is an advisory preparation companion. ScholarPal never performs automated submissions or stores
            portal credentials. When you complete an application on the sponsor's external portal, update the card here
            to <strong>Submitted</strong> to monitor subsequent interview rounds and offers.
          </p>
        </div>
      </div>

      {/* 7-Stage Kanban Board */}
      <div className="kanban-board-scroll">
        <div className="kanban-board">
          {STAGES.map((stage) => {
            const stageApps = applications.filter((a) => a.stage === stage);

            return (
              <div key={stage} className={`kanban-column stage-${stage.toLowerCase()}`}>
                <div className="kanban-column-header">
                  <div className="col-header-title">
                    <span className="col-name">{stage}</span>
                    <span className="col-count">{stageApps.length}</span>
                  </div>
                </div>

                <div className="kanban-cards-list">
                  {stageApps.length === 0 ? (
                    <div className="kanban-empty-slot">No applications</div>
                  ) : (
                    stageApps.map((app) => {
                      const sch = scholarships.find((s) => s.id === app.scholarship_id);
                      const readyDocs = app.checklist.filter((d) => d.is_ready).length;
                      const totalDocs = app.checklist.length;
                      const currentStageIndex = STAGES.indexOf(app.stage);

                      return (
                        <div key={app.id} className="kanban-card">
                          <div className="card-sponsor">{sch?.provider || "Sponsor"}</div>
                          <h4 className="card-sch-title">
                            <Link to={`/scholarships/${app.scholarship_id}`}>
                              {sch?.title || "Scholarship"}
                            </Link>
                          </h4>

                          <div className="card-cycle-badge">
                            Cycle: {sch?.application_cycle || "2026"}
                          </div>

                          {/* Document Readiness Bar */}
                          <div className="card-readiness-wrapper">
                            <ReadinessBar
                              readyCount={readyDocs}
                              totalCount={totalDocs}
                              compact={true}
                            />
                          </div>

                          {/* Portal Submission Reference Tag */}
                          {app.submission_reference && (
                            <div className="card-ref-badge">
                              <span>Ref: </span>
                              <code>{app.submission_reference}</code>
                            </div>
                          )}

                          {/* Interactive Stage Transition Controls */}
                          <div className="card-stage-controls">
                            <div className="stage-select-wrapper">
                              <label className="stage-select-label">Move stage:</label>
                              <select
                                className="stage-select"
                                value={app.stage}
                                onChange={(e) =>
                                  handleMoveStage(app.id, e.target.value as ApplicationStage)
                                }
                              >
                                {STAGES.map((s) => (
                                  <option key={s} value={s}>
                                    {s}
                                  </option>
                                ))}
                              </select>
                            </div>

                            <div className="card-quick-arrows">
                              {currentStageIndex > 0 && (
                                <button
                                  type="button"
                                  className="btn-arrow"
                                  title={`Move back to ${STAGES[currentStageIndex - 1]}`}
                                  onClick={() =>
                                    handleMoveStage(app.id, STAGES[currentStageIndex - 1])
                                  }
                                >
                                  <ArrowLeft size={12} />
                                </button>
                              )}
                              {currentStageIndex < STAGES.length - 1 && (
                                <button
                                  type="button"
                                  className="btn-arrow"
                                  title={`Advance to ${STAGES[currentStageIndex + 1]}`}
                                  onClick={() =>
                                    handleMoveStage(app.id, STAGES[currentStageIndex + 1])
                                  }
                                >
                                  <ArrowRight size={12} />
                                </button>
                              )}
                            </div>
                          </div>

                          <div className="card-bottom-links">
                            <Link
                              to={`/scholarships/${app.scholarship_id}`}
                              className="card-detail-link"
                            >
                              Checklist & Details ↗
                            </Link>
                            {app.stage === ApplicationStage.INTERVIEW && (
                              <Link to="/interviews" className="card-interview-link">
                                Interview Prep
                              </Link>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
