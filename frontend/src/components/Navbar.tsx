import React from "react";
import { Link, useLocation } from "react-router-dom";
import { GraduationCap, Search, ShieldCheck, Home } from "lucide-react";

export const Navbar: React.FC = () => {
  const location = useLocation();

  const navLinks = [
    { to: "/", label: "Home", icon: Home },
    { to: "/scholarships", label: "Scholarships", icon: Search },
    { to: "/admin", label: "Admin Console", icon: ShieldCheck },
  ];

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <GraduationCap className="brand-icon" size={28} />
          <span className="brand-text">ScholarPal</span>
        </Link>
        <nav className="navbar-links">
          {navLinks.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={`nav-link ${location.pathname === to ? "active" : ""}`}
            >
              <Icon size={18} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
};
