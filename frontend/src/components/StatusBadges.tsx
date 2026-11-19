import React from "react";
import {
  FreshnessStatus,
  OverallEligibility,
  RequirementOutcome,
  ApplicationStage,
  EvidenceLabel,
  VersionStatus,
} from "../types";
import { Badge } from "./ui";
import { CheckCircle2, AlertCircle, HelpCircle, XCircle, Clock } from "lucide-react";

export const FreshnessBadge: React.FC<{ status: FreshnessStatus }> = ({ status }) => {
  if (status === FreshnessStatus.FRESH) {
    return (
      <Badge variant="success" className="status-badge">
        <CheckCircle2 size={12} style={{ marginRight: 4 }} /> Fresh & Verified
      </Badge>
    );
  }
  return (
    <Badge variant="warning" className="status-badge">
      <AlertCircle size={12} style={{ marginRight: 4 }} /> Uncertain Freshness
    </Badge>
  );
};

export const OverallEligibilityBadge: React.FC<{ status: OverallEligibility }> = ({ status }) => {
  switch (status) {
    case OverallEligibility.MEETS_RECORDED_REQUIREMENTS:
      return (
        <Badge variant="success" className="eligibility-pill">
          <CheckCircle2 size={14} style={{ marginRight: 4 }} /> Meets recorded requirements
        </Badge>
      );
    case OverallEligibility.NEEDS_CLARIFICATION:
      return (
        <Badge variant="warning" className="eligibility-pill">
          <HelpCircle size={14} style={{ marginRight: 4 }} /> Needs clarification
        </Badge>
      );
    case OverallEligibility.DOES_NOT_MEET_RECORDED_REQUIREMENTS:
      return (
        <Badge variant="danger" className="eligibility-pill">
          <XCircle size={14} style={{ marginRight: 4 }} /> Does not meet recorded requirements
        </Badge>
      );
    default:
      return <Badge variant="neutral">Pending check</Badge>;
  }
};

export const RequirementOutcomeBadge: React.FC<{ outcome: RequirementOutcome }> = ({ outcome }) => {
  switch (outcome) {
    case RequirementOutcome.SATISFIED:
      return (
        <Badge variant="success" className="req-pill">
          <CheckCircle2 size={12} style={{ marginRight: 4 }} /> Satisfied
        </Badge>
      );
    case RequirementOutcome.UNMET:
      return (
        <Badge variant="danger" className="req-pill">
          <XCircle size={12} style={{ marginRight: 4 }} /> Unmet
        </Badge>
      );
    case RequirementOutcome.UNRESOLVED:
      return (
        <Badge variant="warning" className="req-pill">
          <HelpCircle size={12} style={{ marginRight: 4 }} /> Unresolved
        </Badge>
      );
    default:
      return <Badge variant="neutral">Unknown</Badge>;
  }
};

export const StageBadge: React.FC<{ stage: ApplicationStage }> = ({ stage }) => {
  switch (stage) {
    case ApplicationStage.SAVED:
      return <Badge variant="neutral">Saved</Badge>;
    case ApplicationStage.PREPARING:
      return <Badge variant="info">Preparing</Badge>;
    case ApplicationStage.SUBMITTED:
      return <Badge variant="info">Submitted</Badge>;
    case ApplicationStage.INTERVIEW:
      return <Badge variant="warning">Interview</Badge>;
    case ApplicationStage.OFFERED:
      return <Badge variant="success">Offered 🎉</Badge>;
    case ApplicationStage.UNSUCCESSFUL:
      return <Badge variant="danger">Unsuccessful</Badge>;
    case ApplicationStage.WITHDRAWN:
      return <Badge variant="neutral">Withdrawn</Badge>;
    default:
      return <Badge variant="neutral">{stage}</Badge>;
  }
};

export const JevVerdictBadge: React.FC<{ verdict: EvidenceLabel }> = ({ verdict }) => {
  switch (verdict) {
    case EvidenceLabel.SUPPORTED:
      return (
        <Badge variant="success" className="jev-badge">
          <CheckCircle2 size={12} style={{ marginRight: 4 }} /> Supported
        </Badge>
      );
    case EvidenceLabel.CONTRADICTED:
      return (
        <Badge variant="danger" className="jev-badge">
          <XCircle size={12} style={{ marginRight: 4 }} /> Contradicted
        </Badge>
      );
    case EvidenceLabel.UNCLEAR:
      return (
        <Badge variant="warning" className="jev-badge">
          <HelpCircle size={12} style={{ marginRight: 4 }} /> Unclear
        </Badge>
      );
    default:
      return <Badge variant="neutral">{verdict}</Badge>;
  }
};

export const VersionStatusBadge: React.FC<{ status: VersionStatus }> = ({ status }) => {
  switch (status) {
    case VersionStatus.APPROVED:
      return <Badge variant="success">Approved & Published</Badge>;
    case VersionStatus.PENDING:
      return <Badge variant="warning">Pending Review</Badge>;
    case VersionStatus.DEFERRED:
      return <Badge variant="neutral">Deferred</Badge>;
    case VersionStatus.REJECTED:
      return <Badge variant="danger">Rejected</Badge>;
    case VersionStatus.DRAFT:
      return <Badge variant="neutral">Draft</Badge>;
    default:
      return <Badge variant="neutral">{status}</Badge>;
  }
};
