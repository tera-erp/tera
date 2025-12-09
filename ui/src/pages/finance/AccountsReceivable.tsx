import React from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import InvoiceForm from '@/components/finance/InvoiceForm';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, FileText, Plus } from 'lucide-react';
import { useCompany } from '@/context/CompanyContext';

const AccountsReceivable = () => {
  const { activeCompany, activeLocalization } = useCompany();

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <div className="mb-6 flex items-center gap-2 text-sm text-muted-foreground">
        <Link to="/" className="hover:text-foreground transition-colors">
          Dashboard
        </Link>
        <span>/</span>
        <Link to="/" className="hover:text-foreground transition-colors">
          Finance
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">Accounts Receivable</span>
      </div>

      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-blue-600">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Accounts Receivable</h1>
              <p className="text-muted-foreground">
                Customer invoices and receivables management
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

      {/* Company Context */}
      <Card className="mb-6 border-l-4 border-l-blue-500">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Active Entity</CardTitle>
          <CardDescription>
            {activeCompany.name} ({activeCompany.country_code}) · {activeLocalization.eInvoice.system} Compliant
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left - Invoice Calculator */}
        <div className="lg:col-span-1">
          <InvoiceForm />
        </div>

        {/* Right - Invoice List Placeholder */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Customer Invoices</CardTitle>
                <Button size="sm">
                  <Plus className="mr-2 h-4 w-4" />
                  New Invoice
                </Button>
              </div>
              <CardDescription>
                Recent invoices for {activeCompany.name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No invoices yet</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Use the calculator on the left to test tax calculations,<br />
                  or create your first customer invoice.
                </p>
                <Button variant="outline" size="sm">Create First Invoice</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Key Features</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-0.5">✓</span>
                  <span>Real-time tax calculation with {activeLocalization.tax.type} ({activeLocalization.tax.rate})</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-0.5">✓</span>
                  <span>Automatic compliance checks for {activeLocalization.eInvoice.system}</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-0.5">✓</span>
                  <span>Multi-currency support ({activeCompany.currency_code})</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-muted-foreground/40 mt-0.5">○</span>
                  <span className="text-muted-foreground/60">Aging reports (Coming Soon)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-muted-foreground/40 mt-0.5">○</span>
                  <span className="text-muted-foreground/60">Payment reminders (Coming Soon)</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default AccountsReceivable;
