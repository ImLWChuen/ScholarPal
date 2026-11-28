import { createBrowserRouter } from "react-router-dom";
import { Layout } from "../components/Layout";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { DashboardPage } from "../pages/DashboardPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ScholarshipsPage } from "../pages/ScholarshipsPage";
import { ScholarshipDetailPage } from "../pages/ScholarshipDetailPage";
import { ApplicationsPage } from "../pages/ApplicationsPage";
import { InterviewsPage } from "../pages/InterviewsPage";
import { ComparisonPage } from "../pages/ComparisonPage";
import { AdminPage } from "../pages/AdminPage";
import { LoginPage } from "../pages/LoginPage";
import { RegisterPage } from "../pages/RegisterPage";
import { NotFoundPage } from "../pages/NotFoundPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "login",
        element: <LoginPage />,
      },
      {
        path: "register",
        element: <RegisterPage />,
      },
      {
        index: true,
        element: (
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "dashboard",
        element: (
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "profile",
        element: (
          <ProtectedRoute requiredRole="student">
            <ProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: "scholarships",
        element: (
          <ProtectedRoute>
            <ScholarshipsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "scholarships/:id",
        element: (
          <ProtectedRoute>
            <ScholarshipDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "applications",
        element: (
          <ProtectedRoute requiredRole="student">
            <ApplicationsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "interviews",
        element: (
          <ProtectedRoute requiredRole="student">
            <InterviewsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "comparison",
        element: (
          <ProtectedRoute>
            <ComparisonPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "admin",
        element: (
          <ProtectedRoute requiredRole="administrator">
            <AdminPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);
