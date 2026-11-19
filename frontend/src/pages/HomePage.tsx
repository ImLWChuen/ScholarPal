import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchHealth } from "../api/health";
import { Card, Badge, Button } from "../components/ui";
import { Link } from "react-router-dom";
import { CheckCircle2, AlertTriangle, ArrowRight, BookOpen } from "lucide-react";

export const HomePage: React.FC = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 1,
  });

  return (
    <div className="page-home">
      <section className="hero-section">
        <h1>Welcome to ScholarPal</h1>
        <p className="hero-description">
          Intelligent scholarship discovery, deterministic eligibility evaluation,
          and application tracking for Malaysian students.
        </p>
        <div className="hero-actions">
          <Link to="/scholarships">
            <Button size="lg">
              Explore Scholarships <ArrowRight size={18} style={{ marginLeft: 8 }} />
            </Button>
          </Link>
          <Link to="/admin">
            <Button variant="secondary" size="lg">
              Admin Review Console
            </Button>
          </Link>
        </div>
      </section>

      <section className="status-grid">
        <Card title="Backend API Status" subtitle="FastAPI + PostgreSQL connection">
          <div className="status-indicator">
            {isLoading && <Badge variant="neutral">Connecting to API…</Badge>}
            {data?.status === "ok" && (
              <Badge variant="success">
                <CheckCircle2 size={14} style={{ marginRight: 6 }} /> Connected (status: ok)
              </Badge>
            )}
            {isError && (
              <Badge variant="danger">
                <AlertTriangle size={14} style={{ marginRight: 6 }} /> Backend unavailable (ensure uvicorn is running)
              </Badge>
            )}
          </div>
        </Card>

        <Card title="Architecture Principles" subtitle="Deterministic & Privacy-first">
          <ul className="rules-preview">
            <li>Deterministic predefined rules only (never LLM-driven eligibility)</li>
            <li>Three-state evaluation: satisfied, unmet, or unresolved</li>
            <li>Jev evidence checks assist the administrator (never auto-publish)</li>
            <li>Strict student ownership enforced on every endpoint</li>
          </ul>
        </Card>
      </section>
    </div>
  );
};
