import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import InvoiceForm from '@/components/finance/InvoiceForm';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Info } from 'lucide-react';
import { useLocalization } from '@/context/LocalizationContext';

const TestLab = () => {
    const { currentLocalization } = useLocalization();

    return (
        <MainLayout>
            <div className="max-w-4xl mx-auto space-y-8">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Backend Integration Lab</h1>
                    <p className="text-muted-foreground">
                        Testing the connection between React and Python FastAPI.
                    </p>
                </div>

                <Alert className="bg-blue-50 border-blue-200">
                    <Info className="h-4 w-4 text-blue-600" />
                    <AlertTitle className="text-blue-800">Current Context: {currentLocalization.name}</AlertTitle>
                    <AlertDescription className="text-blue-700">
                        Changing the country in the top-right header will instantly change the 
                        tax logic (e.g., 11% PPN vs 9% GST) and payroll laws (BPJS vs CPF).
                    </AlertDescription>
                </Alert>

                <div className="grid md:grid-cols-2 gap-8">
                    <InvoiceForm />
                </div>
            </div>
        </MainLayout>
    );
};

export default TestLab;