import { createBrowserRouter } from "react-router-dom";
import { Layout } from "../components/Layout";
import { DashboardPage } from "../pages/DashboardPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ScholarshipsPage } from "../pages/ScholarshipsPage";
import { ScholarshipDetailPage } from "../pages/ScholarshipDetailPage";
import { ApplicationsPage } from "../pages/ApplicationsPage";
import { InterviewsPage } from "../pages/InterviewsPage";
import { ComparisonPage } from "../pages/ComparisonPage";
import { AdminPage } from "../pages/AdminPage";
import { NotFoundPage } from "../pages/NotFoundPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "dashboard",
        element: <DashboardPage />,
      },
      {
        path: "profile",
        element: <ProfilePage />,
      },
      {
        path: "scholarships",
        element: <ScholarshipsPage />,
      },
      {
        path: "scholarships/:id",
        element: <ScholarshipDetailPage />,
      },
      {
        path: "applications",
        element: <ApplicationsPage />,
      },
      {
        path: "interviews",
        element: <InterviewsPage />,
      },
      {
        path: "comparison",
        element: <ComparisonPage />,
      },
      {
        path: "admin",
        element: <AdminPage />,
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);
