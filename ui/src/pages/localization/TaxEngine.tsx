import React from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import InvoiceForm from '@/components/finance/InvoiceForm';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ArrowLeft, Calculator, Info } from 'lucide-react';
import { useCompany } from '@/context/CompanyContext';

const TaxEngine = () => {
  const { activeCompany, activeLocalization } = useCompany();

  const getTaxDetails = () => {
    switch (activeCompany.country_code) {
      case 'ID':
        return {
          name: 'PPN (Pajak Pertambahan Nilai)',
          rate: '11%',
          features: [
            'Standard rate of 11% on taxable goods and services',
            'VAT return (SPT Masa PPN) compliance',
            'e-Faktur integration support',
            'Export transactions (0% rate)',
            'Luxury goods tax (PPnBM) calculation'
          ]
        };
      case 'SG':
        return {
          name: 'GST (Goods and Services Tax)',
          rate: '9%',
          features: [
            'Standard rate of 9% effective from 2024',
            'Zero-rated and exempt supplies handling',
            'GST F5 return generation',
            'IRAS-compliant tax computation',
            'International services tax treatment'
          ]
        };
      case 'MY':
        return {
          name: 'SST (Sales and Service Tax)',
          rate: '6-10%',
          features: [
            'Sales tax (10%) on manufactured goods',
            'Service tax (6%) on prescribed services',
            'MySST portal integration',
            'Tax exemptions and reliefs',
            'Group relief handling'
          ]
        };
      default:
        return {
          name: 'Tax System',
          rate: 'Variable',
          features: []
        };
    }
  };

  const taxDetails = getTaxDetails();

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <div className="mb-6 flex items-center gap-2 text-sm text-muted-foreground">
        <Link to="/" className="hover:text-foreground transition-colors">
          Dashboard
        </Link>
        <span>/</span>
        <Link to="/" className="hover:text-foreground transition-colors">
          Localization
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">Tax Engine</span>
      </div>

      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-green-500/10 text-green-600">
              <Calculator className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Tax Engine</h1>
              <p className="text-muted-foreground">
                {taxDetails.name} calculation and compliance
              </p>
            </div>
          </div>
          <Link to="/">
            <Button variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </Link>
        </div>
      </div>

      {/* Context Alert */}
      <Alert className="mb-6 border-l-4 border-l-green-500">
        <Info className="h-4 w-4" />
        <AlertTitle>Active Tax Jurisdiction: {activeLocalization.name}</AlertTitle>
        <AlertDescription>
          Currently configured for {activeCompany.name} ({activeCompany.country_code}). 
          Switch companies to test different tax regimes.
        </AlertDescription>
      </Alert>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left - Tax Calculator */}
        <div className="lg:col-span-1">
          <InvoiceForm />
        </div>

        {/* Right - Tax Information */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{taxDetails.name}</CardTitle>
              <CardDescription>
                Tax rate: {taxDetails.rate}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Active Features</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    {taxDetails.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-green-600 mt-0.5">✓</span>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tax Calculation Logic</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="bg-muted/50 p-3 rounded-lg font-mono text-xs">
                  <div className="text-muted-foreground mb-1">// Strategy Pattern Implementation</div>
                  <div>country_code = "{activeCompany.country_code}"</div>
                  <div>tax_strategy = get_strategy(country_code)</div>
                  <div>tax_amount = tax_strategy.calculate_tax(subtotal)</div>
                </div>
                <p className="text-muted-foreground">
                  The tax engine uses a plugin-based architecture where each country's 
                  tax rules are implemented as separate strategies. This allows for 
                  complex jurisdiction-specific logic while maintaining clean, testable code.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Compliance Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm">Tax Calculation Engine</span>
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm">{activeLocalization.eInvoice.system} Integration</span>
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">In Development</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm">Tax Return Filing</span>
                  <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Planned</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default TaxEngine;
