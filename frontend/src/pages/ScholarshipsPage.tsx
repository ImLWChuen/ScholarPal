import React from "react";
import { Card, Badge } from "../components/ui";

export const ScholarshipsPage: React.FC = () => {
  return (
    <div className="page-scholarships">
      <h2>Scholarship Discovery</h2>
      <p className="page-subtitle">
        Browse and filter Malaysian scholarships across SPM, STPM, Matriculation, Undergraduate, and Postgraduate levels.
      </p>

      <Card title="Discovery Pipeline" subtitle="Ingestion via Scrapy + Cleaning via Trafilatura">
        <p>No scholarships loaded yet. The discovery module will be wired to the backend API.</p>
        <div style={{ marginTop: 12 }}>
          <Badge variant="info">Module 2: Scholarship Discovery</Badge>
        </div>
      </Card>
    </div>
  );
};
