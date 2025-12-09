import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { toast } from 'sonner';

// --- Types ---
export interface InvoiceLine {
  product_name: string;
  quantity: number;
  price_unit: number;
}

export interface InvoiceCalculationReq {
  partner_id: number;
  country_code: string;
  lines: InvoiceLine[];
}

export interface InvoiceResponse {
  subtotal: number;
  tax_amount: number;
  tax_name: string;
  total: number;
  compliance_check: boolean;
}

export type DocumentFormat = 'pdf' | 'html' | 'json' | 'xml';

// --- Hook ---
export const useCalculateInvoice = () => {
  return useMutation({
    mutationFn: async (data: InvoiceCalculationReq) => {
      const response = await apiClient.post<InvoiceResponse>('/finance/calculate', data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`Applied Tax: ${data.tax_name}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Calculation failed');
    },
  });
};

/**
 * Hook to download invoice document in specified format
 */
export const useDownloadInvoiceDocument = () => {
  return useMutation({
    mutationFn: async ({ invoiceId, format }: { invoiceId: number; format: DocumentFormat }) => {
      const response = await apiClient.get(`/finance/invoices/${invoiceId}/document?format=${format}`, {
        responseType: 'blob',
      });
      return response.data;
    },
    onSuccess: (blob, variables) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Determine extension based on format
      const extensions: Record<DocumentFormat, string> = {
        pdf: 'pdf',
        html: 'html',
        json: 'json',
        xml: 'xml',
      };
      
      link.download = `invoice_${Date.now()}.${extensions[variables.format]}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success(`Invoice downloaded as ${variables.format.toUpperCase()}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to download invoice');
    },
  });
};