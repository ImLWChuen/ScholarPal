import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  GraduationCap,
  LayoutDashboard,
  User,
  Search,
  KanbanSquare,
  Calendar,
  Scale,
  ShieldCheck,
  LogOut,
  LogIn,
} from "lucide-react";
import { useAuth } from "../features/auth/AuthContext";

export const Navbar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  const navLinks = [
    { to: "/", label: "Dashboard", icon: LayoutDashboard },
    { to: "/profile", label: "Profile", icon: User },
    { to: "/scholarships", label: "Scholarships", icon: Search },
    { to: "/applications", label: "Applications", icon: KanbanSquare },
    { to: "/interviews", label: "Interviews", icon: Calendar },
    { to: "/comparison", label: "Comparison", icon: Scale },
    ...(user?.role === "administrator"
      ? [{ to: "/admin", label: "Admin Console", icon: ShieldCheck }]
      : []),
  ];

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <GraduationCap className="brand-icon" size={26} />
          <span className="brand-text">ScholarPal</span>
        </Link>
        <nav className="navbar-links">
          {isAuthenticated ? (
            <>
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
              <span className="nav-user-pill" title={user?.email}>
                {user?.full_name}
              </span>
              <button
                onClick={handleLogout}
                className="btn-reset-mock"
                title="Sign out"
                type="button"
              >
                <LogOut size={14} />
                <span>Sign Out</span>
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">
                <LogIn size={16} />
                <span>Sign In</span>
              </Link>
              <Link to="/register" className="nav-link">
                <User size={16} />
                <span>Register</span>
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};
