import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../features/auth/AuthContext";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: "student" | "administrator";
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="auth-loading-state" role="status" aria-live="polite">
        <div className="loading-spinner" />
        <p>Verifying your session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return (
      <div className="alert-banner danger-banner" style={{ margin: "2rem auto", maxWidth: 600 }}>
        <span>You do not have permission to access this page ({requiredRole} role required).</span>
      </div>
    );
  }

  return <>{children}</>;
};
