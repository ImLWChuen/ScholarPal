import React, { useState, useEffect } from "react";
import {
  getStoredAdminReviews,
  saveStoredAdminReviews,
  MockAdminReviewItem,
} from "../mock/mockData";
import { EvidenceLabel, VersionStatus } from "../types";
import { Card, Button, Badge } from "../components/ui";
import { JevVerdictBadge, VersionStatusBadge } from "../components/StatusBadges";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  ExternalLink,
  RotateCcw,
  AlertCircle,
  Radio,
  FileCheck,
} from "lucide-react";

export const AdminPage: React.FC = () => {
  const [reviews, setReviews] = useState<MockAdminReviewItem[]>(getStoredAdminReviews());
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    setReviews(getStoredAdminReviews());
  }, []);

  const handleAction = (id: string, newStatus: VersionStatus, actionLabel: string) => {
    const latestReviews = getStoredAdminReviews();
    const updated = latestReviews.map((item) =>
      item.id === id ? { ...item, review_status: newStatus } : item
    );
    setReviews(updated);
    saveStoredAdminReviews(updated);
    setNotification(`Scholarship snapshot ${actionLabel} successfully.`);
    setTimeout(() => setNotification(null), 3500);
  };

  const monitoredSources = [
    {
      name: "Yayasan Khazanah",
      url: "https://www.yayasankhazanah.com.my",
      status: "Active",
      lastCheck: "2026-11-19 14:30 MYT",
      robotsTxt: "Allowed (delay: 2s)",
      method: "Scrapy + Trafilatura",
    },
    {
      name: "Yayasan PETRONAS",
      url: "https://www.yayasanpetronas.com.my",
      status: "Active",
      lastCheck: "2026-11-19 13:45 MYT",
      robotsTxt: "Allowed (no delay)",
      method: "Playwright Rendered",
    },
    {
      name: "Jabatan Perkhidmatan Awam (JPA)",
      url: "https://esilav2.jpa.gov.my",
      status: "Active (Uncertain Freshness)",
      lastCheck: "2026-11-19 11:20 MYT",
      robotsTxt: "Allowed",
      method: "Scrapy + PDF OCR",
    },
    {
      name: "Bank Negara Malaysia (BNM)",
      url: "https://www.bnm.gov.my/careers/scholarships",
      status: "Active",
      lastCheck: "2026-11-19 09:00 MYT",
      robotsTxt: "Allowed",
      method: "Static HTML Feed",
    },
  ];

  return (
    <div className="page-admin">
      <div className="page-header-row">
        <div>
          <h2>Administrator Review Console</h2>
          <p className="page-subtitle">
            Inspect automated source crawls, LLM-extracted criteria snapshots, and Jev Choice primitive evidence verdicts.
          </p>
        </div>
        <div>
          <Badge variant="neutral">Admin Role: Authorized</Badge>
        </div>
      </div>

      {notification && (
        <div className="alert-banner success-banner">
          <CheckCircle2 size={18} />
          <span>{notification}</span>
        </div>
      )}

      {/* Rule 3 Non-Negotiable Human-in-the-Loop Callout */}
      <div className="alert-banner info-banner">
        <ShieldCheck size={24} className="alert-icon" />
        <div className="alert-content">
          <strong>Rule 3 Compliance: Mandatory Human-in-the-Loop Verification</strong>
          <p>
            Automated crawlers and LLM extraction pipelines suggest candidate scholarship criteria, and the Jev Choice
            primitive verifies claim support against original text. However, Jev verdicts <strong>NEVER auto-publish</strong>.
            A human administrator must manually inspect the evidence and explicitly sign off before any version is made public.
          </p>
        </div>
      </div>

      {/* Section 1: Monitored Malaysian Scholarship Sources Table */}
      <Card
        title="Monitored Official Sources"
        subtitle="Crawl schedule, robots.txt compliance, and ingestion pipeline status"
      >
        <div className="sources-table-container">
          <table className="sources-table">
            <thead>
              <tr>
                <th>Source Sponsor</th>
                <th>Portal Target URL</th>
                <th>Status</th>
                <th>Last Crawled</th>
                <th>robots.txt Policy</th>
                <th>Ingestion Pipeline</th>
              </tr>
            </thead>
            <tbody>
              {monitoredSources.map((src, idx) => (
                <tr key={idx}>
                  <td>
                    <strong>{src.name}</strong>
                  </td>
                  <td>
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-link text-sm"
                    >
                      {src.url} <ExternalLink size={12} />
                    </a>
                  </td>
                  <td>
                    {src.status.includes("Uncertain") ? (
                      <Badge variant="warning">{src.status}</Badge>
                    ) : (
                      <Badge variant="success">{src.status}</Badge>
                    )}
                  </td>
                  <td>
                    <span className="text-sm">{src.lastCheck}</span>
                  </td>
                  <td>
                    <span className="text-sm font-mono">{src.robotsTxt}</span>
                  </td>
                  <td>
                    <span className="pipeline-tag">{src.method}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Section 2: Jev Evidence & Candidate Extraction Review Queue */}
      <Card
        title="Candidate Extraction & Jev Evidence Review Queue"
        subtitle="Verify extracted eligibility criteria against official source documents"
      >
        <div className="review-queue-list">
          {reviews.map((rev) => (
            <div key={rev.id} className="review-card">
              <div className="review-card-header">
                <div>
                  <div className="review-meta-line">
                    <span className="provider-name">{rev.provider}</span>
                    <span className="cycle-badge">Cycle: {rev.application_cycle}</span>
                    <VersionStatusBadge status={rev.review_status} />
                  </div>
                  <h3 className="review-title">{rev.scholarship_title}</h3>
                  <a
                    href={rev.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="source-url-link"
                  >
                    Source URL: {rev.source_url} <ExternalLink size={12} />
                  </a>
                </div>

                {/* Jev Choice Primitive Verdict Card */}
                <div className="jev-score-box">
                  <span className="jev-box-label">Jev Choice Primitive Result:</span>
                  <JevVerdictBadge verdict={rev.jev_verdict} />
                  <div className="jev-confidence-score">
                    Confidence: <strong>{(rev.jev_confidence * 100).toFixed(0)}%</strong>
                  </div>
                  <div className="jev-probs-list">
                    <span>
                      sup: {(rev.jev_probabilities.supported * 100).toFixed(0)}%
                    </span>
                    <span>
                      unc: {(rev.jev_probabilities.unclear * 100).toFixed(0)}%
                    </span>
                    <span>
                      con: {(rev.jev_probabilities.contradicted * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Extracted Criteria Preview Table */}
              <div className="extracted-criteria-box">
                <span className="box-title">Extracted Criteria Snapshot:</span>
                <div className="extracted-criteria-list">
                  {rev.extracted_criteria.map((crit, cIdx) => (
                    <div key={cIdx} className="extracted-crit-item">
                      <div className="crit-item-head">
                        <strong>{crit.name}</strong>
                        <code>Rule: {crit.rule}</code>
                      </div>
                      <blockquote className="crit-excerpt">
                        "{crit.source_excerpt}"
                      </blockquote>
                    </div>
                  ))}
                </div>
              </div>

              {/* Administrator Human-in-the-Loop Actions */}
              <div className="review-actions-bar">
                <span className="action-prompt">Administrator Sign-off:</span>
                <div className="action-buttons-group">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleAction(rev.id, VersionStatus.APPROVED, "approved")}
                    disabled={rev.review_status === VersionStatus.APPROVED}
                  >
                    <CheckCircle2 size={14} style={{ marginRight: 4 }} /> Approve Version
                  </Button>

                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleAction(rev.id, VersionStatus.DEFERRED, "deferred for investigation")}
                    disabled={rev.review_status === VersionStatus.DEFERRED}
                  >
                    <HelpCircle size={14} style={{ marginRight: 4 }} /> Defer (Needs Clarification)
                  </Button>

                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleAction(rev.id, VersionStatus.REJECTED, "rejected")}
                    disabled={rev.review_status === VersionStatus.REJECTED}
                  >
                    <XCircle size={14} style={{ marginRight: 4 }} /> Reject Candidate
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
