import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  ArrowLeft,
  Settings as SettingsIcon,
  Building2,
  Globe,
  DollarSign,
  Calendar,
  FileText,
  Users,
  Shield,
  Save,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import { useCompany } from '@/context/CompanyContext';
import { useAuth } from '@/context/AuthContext';
import { localizationConfigs } from '@/config/localization';

const Settings = () => {
  const { activeCompany, activeLocalization } = useCompany();
  const { user } = useAuth();
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [activeTab, setActiveTab] = useState('company');

  // Check if user has admin access based on role from auth context
  const hasAdminAccess = user && (user.role === 'hr_admin' || user.role === 'it_admin');

  // Form state for company settings (will be replaced with API calls in future)
  const [companySettings, setCompanySettings] = useState({
    legalName: activeCompany.name,
    countryCode: activeCompany.country_code,
    currencyCode: activeCompany.currency_code,
    taxId: '201234567K',
    registrationNumber: 'UEN-123456789',
    address: '123 Business Street, #10-01',
    city: 'Singapore',
    postalCode: '123456',
    phone: '+65 6123 4567',
    email: 'contact@tera-erp.com',
  });

  const [localizationSettings, setLocalizationSettings] = useState({
    countryCode: activeCompany.country_code,
    timezone: activeLocalization.timezone,
    dateFormat: 'DD/MM/YYYY',
    fiscalYearStart: '01',
    eInvoiceEnabled: true,
    eInvoiceProvider: activeLocalization.eInvoice.provider,
  });

  const [payrollSettings, setPayrollSettings] = useState({
    payPeriod: 'monthly',
    paymentDay: '25',
    autoCalculateStatutory: true,
    enableOvertimeTracking: true,
    defaultWorkingHours: '8',
  });

  const handleSaveSettings = () => {
    // In real app, this would call an API
    console.log('Saving settings...', { companySettings, localizationSettings, payrollSettings });
    setHasUnsavedChanges(false);
    // Show success message
  };

  if (!hasAdminAccess) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center py-20">
          <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-100">
            <Shield className="h-10 w-10 text-red-600" />
          </div>
          <h2 className="mb-2 text-xl font-semibold text-foreground">Access Denied</h2>
          <p className="mb-6 max-w-md text-center text-muted-foreground">
            You don't have permission to access system settings. 
            Only HR Admins and IT Admins can manage company-wide settings.
          </p>
          <Link to="/">
            <Button variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <div className="mb-6 flex items-center gap-2 text-sm text-muted-foreground">
        <Link to="/" className="hover:text-foreground transition-colors">
          Dashboard
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">Settings</span>
      </div>

      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-blue-600">
              <SettingsIcon className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Company Settings</h1>
              <p className="text-muted-foreground">
                Manage settings for {activeCompany.name}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link to="/">
              <Button variant="outline">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
            </Link>
            {hasUnsavedChanges && (
              <Button onClick={handleSaveSettings} className="bg-blue-600 hover:bg-blue-700">
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Admin Badge */}
      <Alert className="mb-6 border-l-4 border-l-blue-500">
        <Shield className="h-4 w-4" />
        <AlertTitle>Administrator Access</AlertTitle>
        <AlertDescription>
          You are logged in as <span className="font-semibold">{user?.role}</span>.
          Changes made here will affect all users in {activeCompany.name}.
        </AlertDescription>
      </Alert>

      {/* Unsaved Changes Warning */}
      {hasUnsavedChanges && (
        <Alert className="mb-6 border-l-4 border-l-yellow-500 bg-yellow-50">
          <AlertTriangle className="h-4 w-4 text-yellow-600" />
          <AlertTitle className="text-yellow-900">Unsaved Changes</AlertTitle>
          <AlertDescription className="text-yellow-800">
            You have unsaved changes. Don't forget to save before leaving this page.
          </AlertDescription>
        </Alert>
      )}

      {/* Settings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
          <TabsTrigger value="company">Company</TabsTrigger>
          <TabsTrigger value="localization">Localization</TabsTrigger>
          <TabsTrigger value="payroll">Payroll</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
        </TabsList>

        {/* Company Info Tab */}
        <TabsContent value="company" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Company Information</CardTitle>
              </div>
              <CardDescription>
                Basic information about your company entity
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="legalName">Legal Company Name</Label>
                  <Input
                    id="legalName"
                    value={companySettings.legalName}
                    onChange={(e) => {
                      setCompanySettings({ ...companySettings, legalName: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="taxId">Tax ID / VAT Number</Label>
                  <Input
                    id="taxId"
                    value={companySettings.taxId}
                    onChange={(e) => {
                      setCompanySettings({ ...companySettings, taxId: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="regNumber">Registration Number</Label>
                  <Input
                    id="regNumber"
                    value={companySettings.registrationNumber}
                    onChange={(e) => {
                      setCompanySettings({ ...companySettings, registrationNumber: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
              </div>

              <Separator />

              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={companySettings.address}
                    onChange={(e) => {
                      setCompanySettings({ ...companySettings, address: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={companySettings.city}
                    onChange={(e) => {
                      setCompanySettings({ ...companySettings, city: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="postalCode">Postal Code</Label>
                  <Input
                    id="postalCode"
                    value={companySettings.postalCode}
                    onChange={(e) => {
                      setCompanySettings({ ...companySettings, postalCode: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={companySettings.phone}
                    onChange={(e) => {
                      setCompanySettings({ ...companySettings, phone: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={companySettings.email}
                    onChange={(e) => {
                      setCompanySettings({ ...companySettings, email: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Localization Tab */}
        <TabsContent value="localization" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Localization Settings</CardTitle>
              </div>
              <CardDescription>
                Configure country-specific settings and compliance requirements
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Current Localization Display */}
              <div className="rounded-lg border border-border bg-secondary/30 p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{activeLocalization.flag}</span>
                    <div>
                      <h3 className="font-semibold text-lg">{activeLocalization.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {activeLocalization.currency.code} • {activeLocalization.timezone}
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Active
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Tax System:</span>
                    <p className="font-medium">{activeLocalization.taxes[0]?.name} ({activeLocalization.taxes[0]?.rate}%)</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">E-Invoice:</span>
                    <p className="font-medium">{activeLocalization.eInvoice.system}</p>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Change Country Warning */}
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Change Country/Region</AlertTitle>
                <AlertDescription>
                  To change the country/region for this company, contact your system administrator.
                  This requires updating core business logic, tax calculations, and compliance settings.
                </AlertDescription>
              </Alert>

              {/* Regional Settings */}
              <div className="space-y-4">
                <h4 className="font-semibold">Regional Preferences</h4>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="timezone">Timezone</Label>
                    <Select
                      value={localizationSettings.timezone}
                      onValueChange={(value) => {
                        setLocalizationSettings({ ...localizationSettings, timezone: value });
                        setHasUnsavedChanges(true);
                      }}
                    >
                      <SelectTrigger id="timezone">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Asia/Singapore">Asia/Singapore (SGT)</SelectItem>
                        <SelectItem value="Asia/Jakarta">Asia/Jakarta (WIB)</SelectItem>
                        <SelectItem value="Asia/Kuala_Lumpur">Asia/Kuala_Lumpur (MYT)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="dateFormat">Date Format</Label>
                    <Select
                      value={localizationSettings.dateFormat}
                      onValueChange={(value) => {
                        setLocalizationSettings({ ...localizationSettings, dateFormat: value });
                        setHasUnsavedChanges(true);
                      }}
                    >
                      <SelectTrigger id="dateFormat">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                        <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                        <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="fiscalYear">Fiscal Year Start (Month)</Label>
                    <Select
                      value={localizationSettings.fiscalYearStart}
                      onValueChange={(value) => {
                        setLocalizationSettings({ ...localizationSettings, fiscalYearStart: value });
                        setHasUnsavedChanges(true);
                      }}
                    >
                      <SelectTrigger id="fiscalYear">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="01">January</SelectItem>
                        <SelectItem value="04">April</SelectItem>
                        <SelectItem value="07">July</SelectItem>
                        <SelectItem value="10">October</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <Separator />

              {/* E-Invoicing */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">E-Invoicing</h4>
                    <p className="text-sm text-muted-foreground">
                      {activeLocalization.eInvoice.system} integration
                    </p>
                  </div>
                  <Switch
                    checked={localizationSettings.eInvoiceEnabled}
                    onCheckedChange={(checked) => {
                      setLocalizationSettings({ ...localizationSettings, eInvoiceEnabled: checked });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>

                {localizationSettings.eInvoiceEnabled && (
                  <div className="rounded-lg border border-border bg-secondary/20 p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Provider:</span>
                      <span className="font-medium">{activeLocalization.eInvoice.provider}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Status:</span>
                      <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                        Configuration Required
                      </Badge>
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      <FileText className="mr-2 h-4 w-4" />
                      Configure API Credentials
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payroll Tab */}
        <TabsContent value="payroll" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Payroll Settings</CardTitle>
              </div>
              <CardDescription>
                Configure payroll processing and statutory calculations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="payPeriod">Pay Period</Label>
                  <Select
                    value={payrollSettings.payPeriod}
                    onValueChange={(value) => {
                      setPayrollSettings({ ...payrollSettings, payPeriod: value });
                      setHasUnsavedChanges(true);
                    }}
                  >
                    <SelectTrigger id="payPeriod">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="bi-weekly">Bi-weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="paymentDay">Payment Day of Month</Label>
                  <Select
                    value={payrollSettings.paymentDay}
                    onValueChange={(value) => {
                      setPayrollSettings({ ...payrollSettings, paymentDay: value });
                      setHasUnsavedChanges(true);
                    }}
                  >
                    <SelectTrigger id="paymentDay">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {[...Array(28)].map((_, i) => (
                        <SelectItem key={i + 1} value={String(i + 1)}>
                          {i + 1}
                        </SelectItem>
                      ))}
                      <SelectItem value="last">Last Day of Month</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="workingHours">Default Working Hours/Day</Label>
                  <Input
                    id="workingHours"
                    type="number"
                    value={payrollSettings.defaultWorkingHours}
                    onChange={(e) => {
                      setPayrollSettings({ ...payrollSettings, defaultWorkingHours: e.target.value });
                      setHasUnsavedChanges(true);
                    }}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="font-semibold">Statutory Calculations</h4>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium">Auto-calculate Statutory Deductions</p>
                      <p className="text-sm text-muted-foreground">
                        Automatically apply {activeLocalization.name} statutory rates
                      </p>
                    </div>
                    <Switch
                      checked={payrollSettings.autoCalculateStatutory}
                      onCheckedChange={(checked) => {
                        setPayrollSettings({ ...payrollSettings, autoCalculateStatutory: checked });
                        setHasUnsavedChanges(true);
                      }}
                    />
                  </div>

                  <div className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium">Enable Overtime Tracking</p>
                      <p className="text-sm text-muted-foreground">
                        Track and calculate overtime hours
                      </p>
                    </div>
                    <Switch
                      checked={payrollSettings.enableOvertimeTracking}
                      onCheckedChange={(checked) => {
                        setPayrollSettings({ ...payrollSettings, enableOvertimeTracking: checked });
                        setHasUnsavedChanges(true);
                      }}
                    />
                  </div>
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="font-semibold">Current Statutory Rates</h4>
                <div className="space-y-2">
                  {activeLocalization.payroll.map((fund) => (
                    <div
                      key={fund.fund}
                      className="flex items-center justify-between rounded-lg border border-border bg-secondary/30 px-4 py-3"
                    >
                      <span className="font-medium">{fund.fund}</span>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-muted-foreground">
                          Employer: <span className="font-semibold text-foreground">{fund.employerRate}%</span>
                        </span>
                        <span className="text-muted-foreground">
                          Employee: <span className="font-semibold text-foreground">{fund.employeeRate}%</span>
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  * Rates are automatically updated based on official government regulations
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-muted-foreground" />
                <CardTitle>User Management</CardTitle>
              </div>
              <CardDescription>
                Manage user access and permissions for this company
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Users className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">User Management Coming Soon</h3>
                <p className="text-sm text-muted-foreground max-w-md">
                  User role management, permissions, and access control will be available in the next release.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button (Fixed at bottom on mobile) */}
      {hasUnsavedChanges && (
        <div className="fixed bottom-4 right-4 lg:hidden">
          <Button onClick={handleSaveSettings} size="lg" className="bg-blue-600 hover:bg-blue-700 shadow-lg">
            <Save className="mr-2 h-5 w-5" />
            Save Changes
          </Button>
        </div>
      )}
    </MainLayout>
  );
};

export default Settings;
