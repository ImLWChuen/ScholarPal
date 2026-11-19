import React from "react";
import { Outlet } from "react-router-dom";
import { Navbar } from "./Navbar";

export const Layout: React.FC = () => {
  return (
    <div className="app-container">
      <Navbar />
      <main className="content-container">
        <Outlet />
      </main>
      <footer className="footer">
        <div className="footer-container">
          <p>© {new Date().getFullYear()} ScholarPal — Malaysian Scholarship Portal</p>
        </div>
      </footer>
    </div>
  );
};
