// Dynamic localization configuration for Tera
// Countries and their settings are NOT hardcoded - this is a configuration file

export interface TaxConfig {
  code: string;
  name: string;
  rate: number;
  description: string;
}

export interface EInvoiceConfig {
  system: string;
  provider: string;
  mandatory: boolean;
  apiEndpoint?: string;
}

export interface PayrollConfig {
  fund: string;
  employerRate: number;
  employeeRate: number;
  description: string;
}

export interface LocalizationConfig {
  code: string;
  name: string;
  flag: string;
  currency: {
    code: string;
    symbol: string;
    name: string;
  };
  timezone: string;
  locale: string;
  taxes: TaxConfig[];
  eInvoice: EInvoiceConfig;
  payroll: PayrollConfig[];
  fiscalYearEnd: string;
  dateFormat: string;
  accentColor: string;
}

// This configuration can be loaded from an API or database
export const localizationConfigs: LocalizationConfig[] = [
  {
    code: "IDN",
    name: "Indonesia",
    flag: "🇮🇩",
    currency: {
      code: "IDR",
      symbol: "Rp",
      name: "Indonesian Rupiah",
    },
    timezone: "Asia/Jakarta",
    locale: "id-ID",
    taxes: [
      { code: "PPN", name: "Value Added Tax", rate: 11, description: "Standard VAT rate" },
      { code: "PPnBM", name: "Luxury Goods Tax", rate: 10, description: "Luxury goods sales tax" },
      { code: "PPh21", name: "Income Tax Art. 21", rate: 5, description: "Employee income tax" },
      { code: "PPh23", name: "Income Tax Art. 23", rate: 2, description: "Withholding tax for services" },
    ],
    eInvoice: {
      system: "e-Faktur",
      provider: "DJP Online",
      mandatory: true,
      apiEndpoint: "https://efaktur.pajak.go.id",
    },
    payroll: [
      { fund: "BPJS Kesehatan", employerRate: 4, employeeRate: 1, description: "National health insurance" },
      { fund: "BPJS Ketenagakerjaan JKK", employerRate: 0.89, employeeRate: 0, description: "Work accident insurance" },
      { fund: "BPJS Ketenagakerjaan JHT", employerRate: 3.7, employeeRate: 2, description: "Old age security" },
      { fund: "BPJS Ketenagakerjaan JP", employerRate: 2, employeeRate: 1, description: "Pension fund" },
    ],
    fiscalYearEnd: "December",
    dateFormat: "DD/MM/YYYY",
    accentColor: "country-id",
  },
  {
    code: "SGP",
    name: "Singapore",
    flag: "🇸🇬",
    currency: {
      code: "SGD",
      symbol: "S$",
      name: "Singapore Dollar",
    },
    timezone: "Asia/Singapore",
    locale: "en-SG",
    taxes: [
      { code: "GST", name: "Goods and Services Tax", rate: 9, description: "Standard GST rate" },
    ],
    eInvoice: {
      system: "InvoiceNow",
      provider: "Peppol Network",
      mandatory: true,
      apiEndpoint: "https://peppol.gov.sg",
    },
    payroll: [
      { fund: "CPF Ordinary", employerRate: 17, employeeRate: 20, description: "Central Provident Fund - OA" },
      { fund: "CPF Special", employerRate: 0, employeeRate: 0, description: "Central Provident Fund - SA" },
      { fund: "CPF Medisave", employerRate: 0, employeeRate: 0, description: "Central Provident Fund - MA" },
      { fund: "SDL", employerRate: 0.25, employeeRate: 0, description: "Skills Development Levy" },
    ],
    fiscalYearEnd: "December",
    dateFormat: "DD/MM/YYYY",
    accentColor: "country-sg",
  },
  {
    code: "MYS",
    name: "Malaysia",
    flag: "🇲🇾",
    currency: {
      code: "MYR",
      symbol: "RM",
      name: "Malaysian Ringgit",
    },
    timezone: "Asia/Kuala_Lumpur",
    locale: "ms-MY",
    taxes: [
      { code: "SST-S", name: "Sales Tax", rate: 10, description: "Standard sales tax rate" },
      { code: "SST-5", name: "Sales Tax (Reduced)", rate: 5, description: "Reduced sales tax rate" },
      { code: "SVC", name: "Service Tax", rate: 8, description: "Service tax rate" },
    ],
    eInvoice: {
      system: "MyInvois",
      provider: "LHDN",
      mandatory: true,
      apiEndpoint: "https://myinvois.hasil.gov.my",
    },
    payroll: [
      { fund: "EPF", employerRate: 13, employeeRate: 11, description: "Employees Provident Fund" },
      { fund: "SOCSO Contribution", employerRate: 1.75, employeeRate: 0.5, description: "Social Security Organization" },
      { fund: "EIS", employerRate: 0.2, employeeRate: 0.2, description: "Employment Insurance System" },
    ],
    fiscalYearEnd: "December",
    dateFormat: "DD/MM/YYYY",
    accentColor: "country-my",
  },
];

export const getLocalization = (code: string): LocalizationConfig | undefined => {
  return localizationConfigs.find((config) => config.code === code);
};

export const getSupportedCountries = () => {
  return localizationConfigs.map(({ code, name, flag, currency }) => ({
    code,
    name,
    flag,
    currency,
  }));
};
