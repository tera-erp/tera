import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import PayrollSimulator from '@/components/hr/PayrollSimulator';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Users, FileSpreadsheet, Calendar, DollarSign, TrendingUp, AlertCircle, Play, CheckCircle } from 'lucide-react';
import { useCompany } from '@/context/CompanyContext';

interface PayrollRun {
  id: string;
  period: string;
  status: 'completed' | 'pending' | 'failed';
  employees: number;
  totalPayout: number;
  processedDate?: string;
}

const Payroll = () => {
  const { activeCompany, activeLocalization } = useCompany();
  const [activeTab, setActiveTab] = useState('dashboard');

//!TODO Backend Determine payroll system name based company settings!
  const getPayrollSystemName = () => {
    switch (activeCompany.country_code) {
      case 'ID':
        return 'BPJS & PPh 21';
      case 'SG':
        return 'CPF & SDL';
      case 'MY':
        return 'EPF & SOCSO';
      default:
        return 'Statutory Payroll';
    }
  };

  // Mock payroll data - TODO: Replace with actual API calls
  const mockPayrollStats = {
    totalEmployees: 0,
    activePayroll: 0,
    totalGrossPay: 0,
    totalDeductions: 0,
    totalNetPay: 0,
    employerContributions: 0,
  };

  const mockPayrollRuns: PayrollRun[] = [];

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <div className="mb-6 flex items-center gap-2 text-sm text-muted-foreground">
        <Link to="/" className="hover:text-foreground transition-colors">
          Dashboard
        </Link>
        <span>/</span>
        <Link to="/" className="hover:text-foreground transition-colors">
          HR & Payroll
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">Payroll</span>
      </div>

      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600">
              <FileSpreadsheet className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Payroll Processing</h1>
              <p className="text-muted-foreground">
                Statutory payroll calculation with {getPayrollSystemName()}
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
      <Card className="mb-6 border-l-4 border-l-purple-500">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Payroll Configuration</CardTitle>
          <CardDescription>
            {activeCompany.name} ({activeCompany.country_code}) · {getPayrollSystemName()} Compliant
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="simulator">Simulator</TabsTrigger>
          <TabsTrigger value="runs">Payroll Runs</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          {mockPayrollStats.totalEmployees === 0 && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>No Payroll Data Available</AlertTitle>
              <AlertDescription>
                Payroll data will be available once you have employees in the system. Visit the{' '}
                <Link to="/hr/employees" className="underline font-semibold hover:no-underline">
                  Employees
                </Link>
                {' '}page to add employees.
              </AlertDescription>
            </Alert>
          )}

          {/* Stats Grid */}
          {mockPayrollStats.totalEmployees > 0 && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Total Employees</CardDescription>
                <CardTitle className="text-2xl">{mockPayrollStats.totalEmployees}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Users className="h-4 w-4" />
                  <span>Active payroll</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Monthly Gross Pay</CardDescription>
                <CardTitle className="text-2xl">
                  {activeCompany.currency_code} {mockPayrollStats.totalGrossPay.toLocaleString()}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-xs text-green-600">
                  <TrendingUp className="h-4 w-4" />
                  <span>Total payroll cost</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Employee Deductions</CardDescription>
                <CardTitle className="text-2xl">
                  {activeCompany.currency_code} {mockPayrollStats.totalDeductions.toLocaleString()}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-xs text-red-600">
                  <DollarSign className="h-4 w-4" />
                  <span>Statutory contributions</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Net Pay</CardDescription>
                <CardTitle className="text-2xl">
                  {activeCompany.currency_code} {mockPayrollStats.totalNetPay.toLocaleString()}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-xs text-blue-600">
                  <CheckCircle className="h-4 w-4" />
                  <span>Total disbursement</span>
                </div>
              </CardContent>
            </Card>
          </div>
          )}

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Payroll Actions</CardTitle>
              <CardDescription>Common payroll processing tasks</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
                <Button className="w-full bg-purple-600 hover:bg-purple-700">
                  <Play className="mr-2 h-4 w-4" />
                  Run Payroll
                </Button>
                <Link to="/hr/employees" className="w-full">
                  <Button variant="outline" className="w-full">
                    <Users className="mr-2 h-4 w-4" />
                    View Employees
                  </Button>
                </Link>
                <Button variant="outline" className="w-full">
                  <Calendar className="mr-2 h-4 w-4" />
                  Attendance
                </Button>
                <Button variant="outline" className="w-full">
                  <FileSpreadsheet className="mr-2 h-4 w-4" />
                  Reports
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Payroll Runs</CardTitle>
              <CardDescription>Latest payroll processing activities</CardDescription>
            </CardHeader>
            <CardContent>
              {mockPayrollRuns.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FileSpreadsheet className="h-12 w-12 mx-auto mb-2 opacity-20" />
                  <p>No payroll runs yet</p>
                </div>
              ) : (
              <div className="space-y-3">
                {mockPayrollRuns.map((run) => (
                  <div key={run.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                        run.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {run.status === 'completed' ? (
                          <CheckCircle className="h-5 w-5" />
                        ) : (
                          <AlertCircle className="h-5 w-5" />
                        )}
                      </div>
                      <div>
                        <div className="font-medium">{run.period}</div>
                        <div className="text-sm text-muted-foreground">
                          {run.employees} employees · {activeCompany.currency_code} {run.totalPayout.toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={run.status === 'completed' ? 'default' : 'secondary'}>
                        {run.status}
                      </Badge>
                      <Button variant="ghost" size="sm">View</Button>
                    </div>
                  </div>
                ))}
              </div>
              )}
            </CardContent>
          </Card>

          {/* Employer Contributions */}
          <Card>
            <CardHeader>
              <CardTitle>Employer Contributions</CardTitle>
              <CardDescription>Monthly statutory contributions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm">Total Gross Pay</span>
                  <span className="font-mono font-medium">
                    {activeCompany.currency_code} {mockPayrollStats.totalGrossPay.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm text-blue-600">Employer Contributions</span>
                  <span className="font-mono font-medium text-blue-600">
                    +{activeCompany.currency_code} {mockPayrollStats.employerContributions.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 pt-3 border-t-2">
                  <span className="font-semibold">Total Employer Cost</span>
                  <span className="font-mono font-bold text-lg">
                    {activeCompany.currency_code} {(mockPayrollStats.totalGrossPay + mockPayrollStats.employerContributions).toLocaleString()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Simulator Tab */}
        <TabsContent value="simulator" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Left - Payroll Simulator */}
            <div className="lg:col-span-1">
              <PayrollSimulator />
            </div>

            {/* Right - Payroll Information */}
            <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Payroll Runs</CardTitle>
              <CardDescription>
                Monthly payroll processing for {activeCompany.name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Users className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No payroll runs yet</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Use the simulator on the left to test calculations,<br />
                  or process your first payroll run.
                </p>
                <Button variant="outline" size="sm">Start Payroll Run</Button>
              </div>
            </CardContent>
          </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">
                    {activeLocalization.name} Payroll Features
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    {activeCompany.country_code === 'ID' && (
                      <>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>BPJS Kesehatan (Health Insurance) calculation</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>BPJS Ketenagakerjaan (JHT, JP, JKK, JKM)</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>PPh 21 progressive tax with PTKP status support</span>
                        </li>
                      </>
                    )}
                    {activeCompany.country_code === 'SG' && (
                      <>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>CPF calculation based on age brackets</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>SDL (Skills Development Levy) computation</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>Wage ceiling compliance</span>
                        </li>
                      </>
                    )}
                    {activeCompany.country_code === 'MY' && (
                      <>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>EPF (Employee Provident Fund) calculation</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>SOCSO (Social Security) computation</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">✓</span>
                          <span>EIS (Employment Insurance System)</span>
                        </li>
                      </>
                    )}
                    <li className="flex items-start gap-2">
                      <span className="text-muted-foreground/40 mt-0.5">○</span>
                      <span className="text-muted-foreground/60">Batch processing (Coming Soon)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-muted-foreground/40 mt-0.5">○</span>
                      <span className="text-muted-foreground/60">Payslip generation (Coming Soon)</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Payroll Runs Tab */}
        <TabsContent value="runs" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Payroll Runs</CardTitle>
                  <CardDescription>Historical payroll processing records</CardDescription>
                </div>
                <Button className="bg-purple-600 hover:bg-purple-700">
                  <Play className="mr-2 h-4 w-4" />
                  New Payroll Run
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockPayrollRuns.map((run) => (
                  <Card key={run.id} className="border-l-4 border-l-purple-500">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-base flex items-center gap-2">
                            {run.period}
                            <Badge variant={run.status === 'completed' ? 'default' : 'secondary'}>
                              {run.status}
                            </Badge>
                          </CardTitle>
                          <CardDescription className="mt-1">
                            Run ID: {run.id}
                          </CardDescription>
                        </div>
                        <Button variant="outline" size="sm">View Details</Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <div className="text-muted-foreground mb-1">Employees</div>
                          <div className="font-semibold">{run.employees}</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground mb-1">Total Payout</div>
                          <div className="font-semibold">
                            {activeCompany.currency_code} {run.totalPayout.toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-muted-foreground mb-1">Processed Date</div>
                          <div className="font-semibold">
                            {run.processedDate ? new Date(run.processedDate).toLocaleDateString() : 'Not processed'}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </MainLayout>
  );
};

export default Payroll;
