import React, { createContext, useContext, ReactNode, useCallback } from "react";
import { useCompany } from "./CompanyContext"; // Import useCompany
import { LocalizationConfig, localizationConfigs, getLocalization } from "@/config/localization";

interface LocalizationContextType {
  currentLocalization: LocalizationConfig;
  setCountry: (code: string) => void; // This will now switch the company
  availableCountries: LocalizationConfig[];
  formatCurrency: (amount: number) => string;
  formatDate: (date: Date) => string;
}

const LocalizationContext = createContext<LocalizationContextType | undefined>(undefined);

// The provider now simply surfaces the company's localization
export const LocalizationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { activeCompany, switchCompany, availableCompanies } = useCompany();

  // The single source of truth for localization is the active company
  const currentLocalization = activeCompany
    ? (getLocalization(activeCompany.country_code))
    : getLocalization("ID")!;

  // Redefine setCountry to switch the company, finding the first company that matches the country code
  const setCountry = useCallback((code: string) => {
    const targetCompany = availableCompanies.find(c => c.country_code === code);
    if (targetCompany) {
      switchCompany(targetCompany.id);
    } else {
      console.warn(`No company found for country code: ${code}`);
    }
  }, [availableCompanies, switchCompany]);

  const formatCurrency = useCallback((amount: number) => {
    return new Intl.NumberFormat(currentLocalization.locale, {
      style: "currency",
      currency: currentLocalization.currency.code,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount);
  }, [currentLocalization]);

  const formatDate = useCallback((date: Date) => {
    return new Intl.DateTimeFormat(currentLocalization.locale, {
      year: "numeric",
      month: "short",
      day: "numeric",
    }).format(date);
  }, [currentLocalization]);

  return (
    <LocalizationContext.Provider
      value={{
        currentLocalization,
        setCountry,
        availableCountries: localizationConfigs, // Keep this for UI pickers
        formatCurrency,
        formatDate,
      }}
    >
      {children}
    </LocalizationContext.Provider>
  );
};

export const useLocalization = (): LocalizationContextType => {
  const context = useContext(LocalizationContext);
  if (context === undefined) {
    throw new Error("useLocalization must be used within a LocalizationProvider");
  }
  return context;
};
