import React from "react";
import { Badge } from "./ui";

interface ReadinessBarProps {
  readyCount: number;
  totalCount: number;
  showCounts?: boolean;
  compact?: boolean;
}

export const ReadinessBar: React.FC<ReadinessBarProps> = ({
  readyCount,
  totalCount,
  showCounts = true,
  compact = false,
}) => {
  // Edge case per spec: If total is 0 or empty, display "Not Available"
  if (totalCount === 0) {
    return (
      <div className="readiness-container">
        {showCounts && <span className="readiness-label">Document Readiness:</span>}
        <Badge variant="neutral" className="not-available-badge">
          Not Available
        </Badge>
      </div>
    );
  }

  const percentage = Math.min(100, Math.round((readyCount / totalCount) * 100));

  return (
    <div className={`readiness-container ${compact ? "compact" : ""}`}>
      <div className="readiness-header">
        <span className="readiness-label">
          Document Readiness: <strong>{percentage}%</strong>
        </span>
        {showCounts && (
          <span className="readiness-fraction">
            ({readyCount} of {totalCount} ready)
          </span>
        )}
      </div>
      <div className="readiness-track">
        <div
          className={`readiness-fill ${
            percentage === 100 ? "complete" : percentage >= 50 ? "in-progress" : "low"
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
