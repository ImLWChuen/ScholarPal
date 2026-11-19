import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  GraduationCap,
  LayoutDashboard,
  User,
  Search,
  KanbanSquare,
  Calendar,
  Scale,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";
import { resetAllMockData } from "../mock/mockData";

export const Navbar: React.FC = () => {
  const location = useLocation();

  const navLinks = [
    { to: "/", label: "Dashboard", icon: LayoutDashboard },
    { to: "/profile", label: "Profile", icon: User },
    { to: "/scholarships", label: "Scholarships", icon: Search },
    { to: "/applications", label: "Applications", icon: KanbanSquare },
    { to: "/interviews", label: "Interviews", icon: Calendar },
    { to: "/comparison", label: "Comparison", icon: Scale },
    { to: "/admin", label: "Admin Console", icon: ShieldCheck },
  ];

  const handleResetData = () => {
    if (window.confirm("Reset all local wireframe data back to default mock state?")) {
      resetAllMockData();
      window.location.reload();
    }
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <GraduationCap className="brand-icon" size={26} />
          <span className="brand-text">ScholarPal</span>
          <span className="wireframe-pill">Wireframe</span>
        </Link>
        <nav className="navbar-links">
          {navLinks.map(({ to, label, icon: Icon }) => {
            const isActive =
              to === "/"
                ? location.pathname === "/" || location.pathname === "/dashboard"
                : location.pathname.startsWith(to);
            return (
              <Link
                key={to}
                to={to}
                className={`nav-link ${isActive ? "active" : ""}`}
              >
                <Icon size={16} />
                <span>{label}</span>
              </Link>
            );
          })}
          <button
            onClick={handleResetData}
            className="btn-reset-mock"
            title="Reset mock data to initial baseline"
          >
            <RotateCcw size={14} />
            <span>Reset Demo</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
