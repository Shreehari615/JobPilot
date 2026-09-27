import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AdminPage } from './pages/AdminPage';
import { DashboardPage } from './pages/DashboardPage';
import { JobsPage } from './pages/JobsPage';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { ProfilePage } from './pages/ProfilePage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { RegisterPage } from './pages/RegisterPage';
import { ResumePage } from './pages/ResumePage';
import { SavedJobsPage } from './pages/SavedJobsPage';
import { SkillGapPage } from './pages/SkillGapPage';

// Protected Route Wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({
  children,
  adminOnly = false,
}) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-indigo-400">
        <span className="animate-pulse font-medium text-sm">Loading JobPilot AI...</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// Dashboard Layout Wrapper
const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-[#0b0f19]">
      <Navbar />
      <div className="flex flex-1 max-w-7xl w-full mx-auto">
        <Sidebar />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">{children}</main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/"
            element={
              <>
                <Navbar />
                <LandingPage />
              </>
            }
          />
          <Route
            path="/login"
            element={
              <>
                <Navbar />
                <LoginPage />
              </>
            }
          />
          <Route
            path="/register"
            element={
              <>
                <Navbar />
                <RegisterPage />
              </>
            }
          />

          {/* Protected / Dashboard Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <DashboardPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/jobs"
            element={
              <DashboardLayout>
                <JobsPage />
              </DashboardLayout>
            }
          />

          <Route
            path="/recommendations"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <RecommendationsPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/resume"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <ResumePage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/skill-gap"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <SkillGapPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <ProfilePage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/saved"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <SavedJobsPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin"
            element={
              <ProtectedRoute adminOnly>
                <DashboardLayout>
                  <AdminPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          {/* Catch-all fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
