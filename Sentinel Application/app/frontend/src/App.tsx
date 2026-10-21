import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import { Shield, BarChart2, Search, Upload } from "lucide-react";
import "./index.css";

// Secondary pages load on demand so the dashboard's first paint ships less code.
const Analyze = lazy(() => import("./pages/Analyze"));
const Reports = lazy(() => import("./pages/Reports"));

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <nav className="sidebar">
          <div className="sidebar-logo">
            <Shield size={22} strokeWidth={1.5} />
            <span>SENTINEL</span>
          </div>
          <div className="sidebar-tagline">Deepfake Intelligence</div>

          <ul className="nav-links">
            {[
              { to: "/", label: "Dashboard", icon: BarChart2 },
              { to: "/analyze", label: "Analyze", icon: Upload },
              { to: "/reports", label: "Reports", icon: Search },
            ].map(({ to, label, icon: Icon }) => (
              <li key={to}>
                <NavLink to={to} end={to === "/"} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                  <Icon size={16} strokeWidth={1.5} />
                  <span>{label}</span>
                </NavLink>
              </li>
            ))}
          </ul>

          <div className="sidebar-footer">
            <div className="status-dot" />
            <span>System Online</span>
          </div>
        </nav>

        <main className="main-content">
          <Suspense fallback={<div className="loading-bar" />}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analyze" element={<Analyze />} />
              <Route path="/reports" element={<Reports />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </BrowserRouter>
  );
}
