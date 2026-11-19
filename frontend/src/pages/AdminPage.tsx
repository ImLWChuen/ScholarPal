import React from "react";
import { Card, Badge } from "../components/ui";

export const AdminPage: React.FC = () => {
  return (
    <div className="page-admin">
      <h2>Administrator Review Console</h2>
      <p className="page-subtitle">
        Review LLM-extracted scholarship criteria and inspect Jev (Choice primitive) evidence verifications.
      </p>

      <Card
        title="Extraction & Evidence Review"
        subtitle="Rule 3: Jev results assist the administrator and never auto-publish"
      >
        <p>Pending extraction reviews will appear here for manual verification and approval.</p>
        <div style={{ marginTop: 12 }}>
          <Badge variant="warning">Review Status: Pending Admin Approval</Badge>
        </div>
      </Card>
    </div>
  );
};
