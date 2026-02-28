import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useAuth } from "./AuthContext";
import { LocalizationConfig, getLocalization } from "@/config/localization";

// 1. Define the Company Entity
export interface Company {
  id: number;
  name: string;
  country_code: string; // Links to our Localization Config
  currency_code: string;
  logo_url?: string;
}

interface CompanyContextType {
  activeCompany: Company;
  availableCompanies: Company[];
  switchCompany: (companyId: number) => void;
  loading: boolean;
  error: string | null;
  // Helper to get the full localization config for the active company
  activeLocalization: LocalizationConfig; 
}

const CompanyContext = createContext<CompanyContextType | undefined>(undefined);

// Default fallback company - defined outside component to avoid dependency issues
const DEFAULT_FALLBACK: Company = { id: 0, name: "Loading...", country_code: "IDN", currency_code: "IDR" };

export const CompanyProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [availableCompanies, setAvailableCompanies] = useState<Company[]>([]);
  const [activeCompany, setActiveCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch companies from API on mount, only if authenticated
  useEffect(() => {
    if (authLoading) {
      return; // Wait for auth to load
    }

    if (!isAuthenticated) {
      setActiveCompany(DEFAULT_FALLBACK);
      setLoading(false);
      setError(null);
      return; // Don't try to fetch if not authenticated
    }

    const fetchCompanies = async () => {
      try {
        const token = localStorage.getItem("access_token");
        
        if (!token) {
          setError("No authentication token found");
          setLoading(false);
          setActiveCompany(DEFAULT_FALLBACK);
          return;
        }

        setLoading(true);
        const response = await fetch("/api/v1/companies/", {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch companies");
        }

        const companies = await response.json();

        if (!companies || companies.length === 0) {
          throw new Error("No companies available");
        }

        setAvailableCompanies(companies);

        // Load from LocalStorage or default to first company
        const savedId = localStorage.getItem("active_company_id");
        const company = companies.find((c: Company) => c.id === Number(savedId)) || companies[0];
        setActiveCompany(company);
        localStorage.setItem("active_company_id", company.id.toString());
        localStorage.setItem("erp_country_code", company.country_code);
        setError(null);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Error loading companies";
        setError(errorMsg);
        console.error("Error fetching companies:", err);
        // Set fallback on error
        setActiveCompany(DEFAULT_FALLBACK);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanies();
  }, [isAuthenticated, authLoading]);

  const switchCompany = (companyId: number) => {
    const target = availableCompanies.find((c) => c.id === companyId);
    if (target) {
      setActiveCompany(target);
      localStorage.setItem("active_company_id", target.id.toString());
      localStorage.setItem("erp_country_code", target.country_code);
    }
  };

  // Always ensure we have an activeCompany (fallback or real)
  const company = activeCompany || DEFAULT_FALLBACK;
  const isLoading = authLoading || (loading && !activeCompany);

  // Derive the full localization config based on the Company's Country Code
  const activeLocalization = getLocalization(company.country_code) || getLocalization("IDN")!;

  return (
    <CompanyContext.Provider
      value={{
        activeCompany: company,
        availableCompanies,
        switchCompany,
        loading: isLoading,
        error,
        activeLocalization,
      }}
    >
      {children}
    </CompanyContext.Provider>
  );
};

export const useCompany = () => {
  const context = useContext(CompanyContext);
  if (!context) throw new Error("useCompany must be used within CompanyProvider");
  return context;
};