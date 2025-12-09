import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Setup from "./pages/Setup";
import ModulesDashboard from "./pages/ModulesDashboard";
import ModuleScreenPage from "./pages/ModuleScreenPage";
import NotFound from "./pages/NotFound";
import TestLab from "./pages/TestLab";
import Settings from "./pages/Settings";
import ErrorBoundary from "./components/ErrorBoundary";
import { CompanyProvider } from "./context/CompanyContext";
import { LocalizationProvider } from "./context/LocalizationContext";
import { AuthProvider } from "./context/AuthContext";
import { useAuth } from "./context/AuthContext";

const queryClient = new QueryClient();

// Check setup status without using AuthProvider hooks
const checkSetupStatus = async () => {
  try {
    const response = await fetch('/api/v1/users/setup/status');
    if (!response.ok) {
      throw new Error('Failed to check setup status');
    }
    return await response.json();
  } catch (err) {
    console.error('Error checking setup status:', err);
    return { is_initialized: false, admin_exists: false };
  }
};

// Setup check wrapper - independent of AuthProvider
const AppWithSetupCheck = () => {
  const [setupNeeded, setSetupNeeded] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSetup = async () => {
      try {
        const status = await checkSetupStatus();
        setSetupNeeded(!status.is_initialized);
      } catch (err) {
        console.error("Failed to check setup status:", err);
        setSetupNeeded(false);
      } finally {
        setLoading(false);
      }
    };

    checkSetup();
  }, []);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (setupNeeded) {
    return <Setup />;
  }

  return <AppRoutes />;
};

// Protected route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

const AppRoutes = () => (
  <Routes>
    {/* Public routes */}
    <Route path="/setup" element={<Setup />} />
    <Route path="/login" element={<Login />} />
    
    <Route
      path="/"
      element={
        <ProtectedRoute>
          <Index />
        </ProtectedRoute>
      }
    />

    {/* Dynamic Module System */}
    <Route
      path="/modules"
      element={
        <ProtectedRoute>
          <ModulesDashboard />
        </ProtectedRoute>
      }
    />
    <Route
      path="/modules/:moduleId/*"
      element={
        <ProtectedRoute>
          <ModuleScreenPage />
        </ProtectedRoute>
      }
    />
    
    <Route path="/test-lab" element={<TestLab />} />
    
    {/* Settings - Admin Only */}
    <Route
      path="/settings"
      element={
        <ProtectedRoute>
          <Settings />
        </ProtectedRoute>
      }
    />
    <Route path="/help" element={<NotFound />} />
    
    {/* Catch-all */}
    <Route path="*" element={<NotFound />} />
  </Routes>
);

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <CompanyProvider>
            <LocalizationProvider>
              <TooltipProvider>
                <Toaster />
                <Sonner />
                <AppWithSetupCheck />
              </TooltipProvider>
            </LocalizationProvider>
          </CompanyProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;
