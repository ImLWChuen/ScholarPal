import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getStoredScholarships,
  getStoredProfile,
  getStoredComparisonIds,
  saveStoredComparisonIds,
  evaluateEligibility,
  MockScholarship,
} from "../mock/mockData";
import { FreshnessStatus, ScholarshipStatus, StudyLevel } from "../types";
import { Card, Button, Input, Badge } from "../components/ui";
import { FreshnessBadge, OverallEligibilityBadge } from "../components/StatusBadges";
import {
  Search,
  Filter,
  ExternalLink,
  Scale,
  CheckCircle2,
  Calendar,
  Clock,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";

export const ScholarshipsPage: React.FC = () => {
  const [scholarships, setScholarships] = useState<MockScholarship[]>(getStoredScholarships());
  const [profile] = useState(getStoredProfile());
  const [comparisonIds, setComparisonIds] = useState<string[]>(getStoredComparisonIds());

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [studyLevelFilter, setStudyLevelFilter] = useState<string>("ALL");
  const [freshnessFilter, setFreshnessFilter] = useState<string>("ALL");

  useEffect(() => {
    setScholarships(getStoredScholarships());
    setComparisonIds(getStoredComparisonIds());
  }, []);

  const handleToggleCompare = (id: string) => {
    let updated: string[];
    if (comparisonIds.includes(id)) {
      updated = comparisonIds.filter((item) => item !== id);
    } else {
      if (comparisonIds.length >= 3) {
        alert("Comparison is limited to a maximum of 3 scholarships at a time.");
        return;
      }
      updated = [...comparisonIds, id];
    }
    setComparisonIds(updated);
    saveStoredComparisonIds(updated);
  };

  const filtered = scholarships.filter((s) => {
    const matchesSearch =
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.provider.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.field_of_study.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesLevel =
      studyLevelFilter === "ALL" || s.study_level === studyLevelFilter;

    const matchesFreshness =
      freshnessFilter === "ALL" || s.freshness === freshnessFilter;

    return matchesSearch && matchesLevel && matchesFreshness;
  });

  return (
    <div className="page-scholarships">
      <div className="page-header-row">
        <div>
          <h2>Malaysian Scholarship Directory</h2>
          <p className="page-subtitle">
            Curated from official portals (Yayasan Khazanah, Yayasan PETRONAS, JPA, BNM) with verified freshness and deterministic criteria.
          </p>
        </div>

        {/* Floating / Header Compare Tray */}
        <div className="compare-tray-pill">
          <Scale size={16} />
          <span>Compare Queue: <strong>{comparisonIds.length}/3</strong></span>
          {comparisonIds.length > 0 && (
            <Link to="/comparison">
              <Button size="sm">
                Compare Now ({comparisonIds.length})
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="filter-bar-card">
        <div className="search-input-wrapper">
          <Search size={18} className="search-icon" />
          <Input
            placeholder="Search by scholarship title, sponsor, or field of study…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filters-row">
          <div className="filter-item">
            <label className="filter-label">Study Level:</label>
            <select
              className="filter-select"
              value={studyLevelFilter}
              onChange={(e) => setStudyLevelFilter(e.target.value)}
            >
              <option value="ALL">All Levels</option>
              <option value={StudyLevel.UNDERGRADUATE}>Undergraduate</option>
              <option value={StudyLevel.POSTGRADUATE}>Postgraduate</option>
              <option value={StudyLevel.PRE_UNIVERSITY}>Pre-University</option>
              <option value={StudyLevel.SECONDARY}>Secondary</option>
            </select>
          </div>

          <div className="filter-item">
            <label className="filter-label">Freshness Status:</label>
            <select
              className="filter-select"
              value={freshnessFilter}
              onChange={(e) => setFreshnessFilter(e.target.value)}
            >
              <option value="ALL">All Freshness</option>
              <option value={FreshnessStatus.FRESH}>Fresh & Verified Only</option>
              <option value={FreshnessStatus.UNCERTAIN}>Uncertain Freshness</option>
            </select>
          </div>

          <span className="results-count">
            Showing {filtered.length} of {scholarships.length} scholarships
          </span>
        </div>
      </div>

      {/* Scholarship Cards Grid */}
      <div className="scholarships-grid">
        {filtered.map((sch) => {
          const evalResult = evaluateEligibility(sch, profile);
          const isComparing = comparisonIds.includes(sch.id);

          return (
            <div key={sch.id} className="scholarship-card">
              {/* Card Top Metadata */}
              <div className="card-top-meta">
                <div className="meta-left">
                  <span className="provider-name">{sch.provider}</span>
                  <span className="cycle-badge">{sch.application_cycle}</span>
                </div>
                <FreshnessBadge status={sch.freshness} />
              </div>

              {/* Title & Core Details */}
              <h3 className="scholarship-title">
                <Link to={`/scholarships/${sch.id}`}>{sch.title}</Link>
              </h3>

              <div className="card-attributes">
                <div className="attr-row">
                  <span className="attr-label">Study Level:</span>
                  <span className="attr-val">{sch.study_level}</span>
                </div>
                <div className="attr-row">
                  <span className="attr-label">Target Fields:</span>
                  <span className="attr-val line-clamp-1">{sch.field_of_study}</span>
                </div>
                <div className="attr-row">
                  <span className="attr-label">Financial Value:</span>
                  <span className="attr-val line-clamp-1">{sch.coverage_summary}</span>
                </div>
                <div className="attr-row">
                  <span className="attr-label">Service Bond:</span>
                  <span className="attr-val">{sch.bond_duration_years} years obligation</span>
                </div>
              </div>

              {/* Freshness & Crawl Timestamps (Section 5.3) */}
              <div className="timestamps-box">
                <div className="timestamp-row">
                  <Clock size={12} />
                  <span>Last Checked: {sch.last_successful_check}</span>
                </div>
                <div className="timestamp-row">
                  <Calendar size={12} />
                  <span>Last Human Review: {sch.last_review_at}</span>
                </div>
              </div>

              {/* Deterministic Eligibility Pill */}
              <div className="eligibility-eval-box">
                <span className="eval-heading">Rule 2 Match with Your Profile:</span>
                <OverallEligibilityBadge status={evalResult.overall} />
              </div>

              {/* Footer Actions */}
              <div className="card-footer-actions">
                <button
                  type="button"
                  className={`btn-compare ${isComparing ? "selected" : ""}`}
                  onClick={() => handleToggleCompare(sch.id)}
                >
                  <Scale size={14} />
                  <span>{isComparing ? "Comparing ✓" : "Compare"}</span>
                </button>

                <div className="footer-right-links">
                  <a
                    href={sch.official_portal_url}
                    target="_blank"
                    rel="noreferrer"
                    className="portal-link-btn"
                    title="External Official Submission Portal (Rule 7)"
                  >
                    Portal <ExternalLink size={12} />
                  </a>

                  <Link to={`/scholarships/${sch.id}`}>
                    <Button size="sm">
                      Details & What-If <ArrowRight size={14} style={{ marginLeft: 4 }} />
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
