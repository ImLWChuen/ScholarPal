import React from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui";

export const NotFoundPage: React.FC = () => {
  return (
    <div className="page-not-found" style={{ textAlign: "center", padding: "4rem 0" }}>
      <h2>404 - Page Not Found</h2>
      <p style={{ margin: "1rem 0 2rem" }}>The requested page does not exist.</p>
      <Link to="/">
        <Button>Return to Home</Button>
      </Link>
    </div>
  );
};
