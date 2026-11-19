import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getStoredScholarships,
  getStoredComparisonIds,
  saveStoredComparisonIds,
  getStoredApplications,
  MockScholarship,
  MockApplication,
} from "../mock/mockData";
import { Card, Button, Input, Badge } from "../components/ui";
import { ReadinessBar } from "../components/ReadinessBar";
import { FreshnessBadge } from "../components/StatusBadges";
import {
  Scale,
  Plus,
  Trash2,
  DollarSign,
  Briefcase,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ExternalLink,
} from "lucide-react";

export interface ComparisonOption {
  id: string;
  title: string;
  provider: string;
  isPersonalOffer?: boolean;
  tuitionCovered: boolean;
  monthlyAllowance: number;
  totalAnnualSupport: number;
  estimatedAnnualCost: number;
  bondYears: number;
  bondNotes: string;
  renewalCriteria: string;
  applicationCycle: string;
  officialPortalUrl?: string;
  readyDocs: number;
  totalDocs: number;
}

export const ComparisonPage: React.FC = () => {
  const [allScholarships] = useState<MockScholarship[]>(getStoredScholarships());
  const [comparisonIds, setComparisonIds] = useState<string[]>(getStoredComparisonIds());
  const [applications] = useState<MockApplication[]>(getStoredApplications());

  // Personal Custom Award Offer state
  const [includePersonalOffer, setIncludePersonalOffer] = useState<boolean>(false);
  const [personalOfferTitle, setPersonalOfferTitle] = useState<string>(
    "USM Vice-Chancellor Merit Grant"
  );
  const [personalOfferProvider, setPersonalOfferProvider] = useState<string>(
    "Universiti Sains Malaysia"
  );
  const [personalTuitionCovered, setPersonalTuitionCovered] = useState<boolean>(true);
  const [personalAllowance, setPersonalAllowance] = useState<number>(1200);
  const [personalAnnualCost, setPersonalAnnualCost] = useState<number>(35000);
  const [personalBondYears, setPersonalBondYears] = useState<number>(0);
  const [personalBondNotes, setPersonalBondNotes] = useState<string>(
    "No bond obligation. Must assist faculty 4 hours/week."
  );
  const [personalRenewal, setPersonalRenewal] = useState<string>(
    "Maintain minimum CGPA 3.67 each semester."
  );

  useEffect(() => {
    setComparisonIds(getStoredComparisonIds());
  }, []);

  const handleRemoveScholarship = (id: string) => {
    const updated = comparisonIds.filter((item) => item !== id);
    setComparisonIds(updated);
    saveStoredComparisonIds(updated);
  };

  const handleAddScholarship = (id: string) => {
    if (comparisonIds.length >= 3) {
      alert("A maximum of 3 options can be compared simultaneously.");
      return;
    }
    if (!comparisonIds.includes(id)) {
      const updated = [...comparisonIds, id];
      setComparisonIds(updated);
      saveStoredComparisonIds(updated);
    }
  };

  // Build list of active options to compare
  const comparedOptions: ComparisonOption[] = [];

  comparisonIds.slice(0, 3).forEach((schId) => {
    const sch = allScholarships.find((s) => s.id === schId);
    if (sch) {
      const app = applications.find((a) => a.scholarship_id === sch.id);
      const readyDocs = app ? app.checklist.filter((c) => c.is_ready).length : 0;
      const totalDocs = sch.required_documents.length;
      const annualAllowance = sch.monthly_allowance * 12;
      const totalAnnualSupport = annualAllowance + (sch.tuition_covered ? 20000 : 0);

      comparedOptions.push({
        id: sch.id,
        title: sch.title,
        provider: sch.provider,
        isPersonalOffer: false,
        tuitionCovered: sch.tuition_covered,
        monthlyAllowance: sch.monthly_allowance,
        totalAnnualSupport,
        estimatedAnnualCost: sch.estimated_annual_cost,
        bondYears: sch.bond_duration_years,
        bondNotes: sch.service_obligation_notes,
        renewalCriteria: sch.renewal_conditions,
        applicationCycle: sch.application_cycle,
        officialPortalUrl: sch.official_portal_url,
        readyDocs,
        totalDocs,
      });
    }
  });

  // If user enabled personal offer, append it if space allows (or replace 3rd)
  if (includePersonalOffer && comparedOptions.length < 3) {
    const annualAllowance = personalAllowance * 12;
    const totalAnnualSupport = annualAllowance + (personalTuitionCovered ? 18000 : 0);

    comparedOptions.push({
      id: "personal-offer-custom",
      title: personalOfferTitle,
      provider: personalOfferProvider,
      isPersonalOffer: true,
      tuitionCovered: personalTuitionCovered,
      monthlyAllowance: personalAllowance,
      totalAnnualSupport,
      estimatedAnnualCost: personalAnnualCost,
      bondYears: personalBondYears,
      bondNotes: personalBondNotes,
      renewalCriteria: personalRenewal,
      applicationCycle: "Direct Faculty Offer",
      readyDocs: 3,
      totalDocs: 3,
    });
  }

  // Calculate estimated funding gap: max(0, Estimated Costs - Applicable Funding)
  const calculateFundingGap = (annualCost: number, annualSupport: number) => {
    return Math.max(0, annualCost - annualSupport);
  };

  return (
    <div className="page-comparison">
      <div className="page-header-row">
        <div>
          <h2>Multi-Option Comparison Matrix</h2>
          <p className="page-subtitle">
            Side-by-side analysis for up to three scholarships or personal award offers. Evaluate funding gaps and service bonds.
          </p>
        </div>
        <div className="page-header-actions">
          <label className="toggle-switch-label">
            <input
              type="checkbox"
              checked={includePersonalOffer}
              onChange={(e) => setIncludePersonalOffer(e.target.checked)}
            />
            <span>Include Personal Offer Letter</span>
          </label>
        </div>
      </div>

      {/* Selectors Bar */}
      <div className="comparison-selectors-card">
        <span className="selector-title">Add Scholarship to Compare ({comparedOptions.length}/3):</span>
        <div className="selectors-list">
          {allScholarships.map((sch) => {
            const isSelected = comparisonIds.includes(sch.id);
            return (
              <button
                key={sch.id}
                type="button"
                className={`selector-chip ${isSelected ? "selected" : ""}`}
                onClick={() =>
                  isSelected ? handleRemoveScholarship(sch.id) : handleAddScholarship(sch.id)
                }
              >
                <span>{sch.title}</span>
                {isSelected ? <Trash2 size={12} /> : <Plus size={12} />}
              </button>
            );
          })}
        </div>
      </div>

      {comparedOptions.length === 0 ? (
        <Card>
          <div className="empty-comparison-state">
            <Scale size={40} className="text-muted" />
            <h4>No Scholarships Selected for Comparison</h4>
            <p>Select at least one scholarship above or from the directory to inspect side-by-side metrics.</p>
            <Link to="/scholarships">
              <Button size="sm">Browse Scholarship Directory</Button>
            </Link>
          </div>
        </Card>
      ) : (
        <div className="matrix-table-container">
          <table className="matrix-table">
            <thead>
              <tr>
                <th className="feature-col">Evaluation Metric</th>
                {comparedOptions.map((opt) => (
                  <th key={opt.id} className="option-col">
                    <div className="opt-header">
                      {opt.isPersonalOffer ? (
                        <Badge variant="warning">Personal Offer</Badge>
                      ) : (
                        <Badge variant="neutral">{opt.applicationCycle}</Badge>
                      )}
                      <h4>{opt.title}</h4>
                      <span className="opt-sponsor">{opt.provider}</span>
                      {!opt.isPersonalOffer && (
                        <button
                          type="button"
                          className="btn-remove-col"
                          onClick={() => handleRemoveScholarship(opt.id)}
                          title="Remove column"
                        >
                          <Trash2 size={14} /> Remove
                        </button>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {/* Row 1: Estimated Annual Costs */}
              <tr>
                <td className="feature-label">
                  <strong>Estimated Annual Cost</strong>
                  <span className="feature-sub">Tuition + estimated living expenses</span>
                </td>
                {comparedOptions.map((opt) => (
                  <td key={opt.id}>
                    <span className="metric-figure">
                      RM {opt.estimatedAnnualCost.toLocaleString()} / year
                    </span>
                  </td>
                ))}
              </tr>

              {/* Row 2: Applicable Funding / Annual Support */}
              <tr>
                <td className="feature-label">
                  <strong>Applicable Annual Support</strong>
                  <span className="feature-sub">Tuition coverage + monthly allowances</span>
                </td>
                {comparedOptions.map((opt) => (
                  <td key={opt.id}>
                    <span className="metric-figure highlight-green">
                      RM {opt.totalAnnualSupport.toLocaleString()} / year
                    </span>
                    <span className="metric-sub">
                      (RM {opt.monthlyAllowance.toLocaleString()}/mo allowance +{" "}
                      {opt.tuitionCovered ? "100% Tuition" : "Partial Tuition"})
                    </span>
                  </td>
                ))}
              </tr>

              {/* Row 3: Estimated Funding Gap Formula */}
              <tr className="row-funding-gap">
                <td className="feature-label">
                  <strong>Estimated Funding Gap</strong>
                  <span className="feature-sub">
                    Formula: <code>max(0, Relevant Costs - Funding)</code>
                  </span>
                </td>
                {comparedOptions.map((opt) => {
                  const gap = calculateFundingGap(
                    opt.estimatedAnnualCost,
                    opt.totalAnnualSupport
                  );
                  return (
                    <td key={opt.id}>
                      {gap === 0 ? (
                        <Badge variant="success" className="gap-badge">
                          <CheckCircle2 size={14} style={{ marginRight: 4 }} /> RM 0 Gap (Fully Funded)
                        </Badge>
                      ) : (
                        <Badge variant="danger" className="gap-badge">
                          <AlertTriangle size={14} style={{ marginRight: 4 }} /> RM{" "}
                          {gap.toLocaleString()} / year Shortfall
                        </Badge>
                      )}
                    </td>
                  );
                })}
              </tr>

              {/* Row 4: Service Bond Duration */}
              <tr>
                <td className="feature-label">
                  <strong>Service Bond Obligation</strong>
                  <span className="feature-sub">Mandatory service years upon graduation</span>
                </td>
                {comparedOptions.map((opt) => (
                  <td key={opt.id}>
                    {opt.bondYears > 0 ? (
                      <div>
                        <strong style={{ color: "var(--warning)" }}>
                          {opt.bondYears} Years Service Bond
                        </strong>
                        <p className="cell-note">{opt.bondNotes}</p>
                      </div>
                    ) : (
                      <div>
                        <Badge variant="success">Bond-Free (0 Years)</Badge>
                        <p className="cell-note">{opt.bondNotes}</p>
                      </div>
                    )}
                  </td>
                ))}
              </tr>

              {/* Row 5: Academic Renewal Conditions */}
              <tr>
                <td className="feature-label">
                  <strong>Renewal Conditions</strong>
                  <span className="feature-sub">Minimum semester academic threshold</span>
                </td>
                {comparedOptions.map((opt) => (
                  <td key={opt.id}>
                    <span>{opt.renewalCriteria}</span>
                  </td>
                ))}
              </tr>

              {/* Row 6: Document Readiness */}
              <tr>
                <td className="feature-label">
                  <strong>Document Readiness</strong>
                  <span className="feature-sub">Formula: Ready / Total Known * 100%</span>
                </td>
                {comparedOptions.map((opt) => (
                  <td key={opt.id}>
                    <ReadinessBar readyCount={opt.readyDocs} totalCount={opt.totalDocs} compact />
                  </td>
                ))}
              </tr>

              {/* Row 7: Actions */}
              <tr>
                <td className="feature-label">
                  <strong>Actions</strong>
                </td>
                {comparedOptions.map((opt) => (
                  <td key={opt.id}>
                    {!opt.isPersonalOffer ? (
                      <div className="action-buttons-cell">
                        <Link to={`/scholarships/${opt.id}`}>
                          <Button size="sm">View Detail & What-If</Button>
                        </Link>
                        {opt.officialPortalUrl && (
                          <a
                            href={opt.officialPortalUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="text-link text-sm"
                          >
                            Official Portal <ExternalLink size={12} />
                          </a>
                        )}
                      </div>
                    ) : (
                      <Badge variant="neutral">Personal Fixture</Badge>
                    )}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
