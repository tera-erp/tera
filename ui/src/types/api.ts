// Matches Pydantic: InvoiceLineItem
export interface InvoiceLineItem {
  product_name: string;
  quantity: number;
  price_unit: number;
}

// Matches Pydantic: InvoiceCreateRequest
export interface InvoiceCreateRequest {
  partner_id: number;
  country_code: string;
  lines: InvoiceLineItem[];
}

// Matches Pydantic: InvoiceResponse
export interface InvoiceResponse {
  subtotal: number;
  tax_amount: number;
  total: number;
  tax_name: string;
  compliance_check: boolean;
}

// Matches Pydantic: PayslipRequest
export interface PayslipRequest {
    country_code: string;
    gross_salary: number;
    age: number;
    is_resident: boolean;
    ptkp_status?: string; // For Indonesia: TK0, K0, K1, K2, K3
}

// Response from payroll calculation
export interface PayslipResponse {
    gross_pay: number;
    employee_deduction: number;
    employer_contribution: number;
    net_pay: number;
    details: Record<string, number>;
}