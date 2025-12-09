import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { PayslipRequest, PayslipResponse } from '@/types/api';
import { toast } from 'sonner';

export const useCalculatePayslip = () => {
  return useMutation({
    mutationFn: async (data: PayslipRequest): Promise<PayslipResponse> => {
      const response = await apiClient.post<PayslipResponse>('/payroll/calculate-preview', data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`Net Pay: ${data.net_pay.toFixed(2)}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Payroll calculation failed');
    },
  });
};