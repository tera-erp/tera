import React, { useState, useEffect } from 'react';
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
import { ModuleFactory } from '@/modules/ModuleFactory';
import { ModuleMetadata, ModuleConfig } from '@/modules/types';

const Settings = () => {
  const { activeCompany, activeLocalization } = useCompany();
  const { user } = useAuth();
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [activeTab, setActiveTab] = useState('company');
  const [modules, setModules] = useState<ModuleMetadata[]>([]);
  const [modulesLoading, setModulesLoading] = useState(false);
  const [moduleMessages, setModuleMessages] = useState<Record<string, string>>({});
  const [editableConfigs, setEditableConfigs] = useState<Record<string, Record<string, unknown>>>({});

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

  

  const handleSaveSettings = () => {
    // In real app, this would call an API
    console.log('Saving settings...', { companySettings, localizationSettings });
    setHasUnsavedChanges(false);
    // Show success message
  };

  // Load modules and find those exposing `configurables`
  useEffect(() => {
    let mounted = true;
    const load = async () => {
      setModulesLoading(true);
      try {
        // Try to get already-registered modules first
        let regs: ModuleMetadata[] = ModuleFactory.getAllModules();
        if (!regs || regs.length === 0) {
          // Fallback: fetch from API via factory
          regs = await ModuleFactory.loadModules();
        }

        if (!mounted) return;

        // Only keep modules that declare `configurables` in their config
        const modsWithConfig = regs
          .map((m) => m.config || (m as unknown as ModuleConfig))
          .filter((c: ModuleConfig) => c && (Boolean((c as unknown as Record<string, unknown>).configurables) || Object.keys(c).includes('configurables')))
          .map((c: ModuleConfig) => ({ module: c.module, config: c }));

        setModules(modsWithConfig);

        // Pre-fill editableConfigs with current values
        const initial: Record<string, Record<string, unknown>> = {};
        modsWithConfig.forEach((m) => {
          const cfg = (m.config as unknown as Record<string, unknown>).configurables as unknown;
          if (!cfg) return;
          // configurables may be array or object
          if (Array.isArray(cfg)) {
            initial[m.module.id] = {};
            (cfg as Array<Record<string, unknown>>).forEach((item) => {
              const key = (item['key'] as string) || (item['id'] as string);
              const val = (item['value'] ?? item['default']) as unknown ?? '';
              initial[m.module.id][key] = val;
            });
          } else {
            initial[m.module.id] = {};
            Object.entries(cfg as Record<string, Record<string, unknown>>).forEach(([k, v]) => {
              const vv = v as Record<string, unknown>;
              const val = (vv.value ?? vv.default) as unknown ?? '';
              initial[m.module.id][k] = val;
            });
          }
        });
        setEditableConfigs(initial);
        // Fetch persisted values for each module and merge
        for (const m of modsWithConfig) {
          const moduleId = m.module.id;
          try {
            const resp = await fetch(`/api/v1/modules/${moduleId}/configurables`, {
              headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
            });
            if (!resp.ok) continue;
            const body = await resp.json();
            const values = body?.values || {};
            setEditableConfigs((prev) => ({ ...prev, [moduleId]: { ...(prev[moduleId] || {}), ...values } }));
          } catch (e) {
            // ignore per-module errors
            console.debug('Failed to fetch persisted configurables for', m.module.id, e);
          }
        }
      } catch (err) {
        console.error('Failed to load modules for settings', err);
      } finally {
        setModulesLoading(false);
      }
    };

    load();
    return () => { mounted = false; };
  }, []);

  const setModuleMessage = (moduleId: string, msg: string) => {
    setModuleMessages((prev) => ({ ...prev, [moduleId]: msg }));
  };

  const handleSaveModuleConfigurables = async (moduleId: string) => {
    const payload = editableConfigs[moduleId] || {};
    setModuleMessage(moduleId, 'Saving...');
    try {
      const res = await fetch(`/api/v1/modules/${moduleId}/configurables`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw new Error(body || `Status ${res.status}`);
      }
      setModuleMessage(moduleId, 'Saved successfully');
    } catch (err) {
      console.error('Save module config failed', err);
      const msg = err instanceof Error ? err.message : String(err);
      setModuleMessage(moduleId, `Save failed: ${msg}`);
    }
    setTimeout(() => setModuleMessage(moduleId, ''), 3000);
  };

  const handleFixModule = async (moduleId: string) => {
    setModuleMessage(moduleId, 'Running fix...');
    try {
      const res = await fetch(`/api/v1/modules/${moduleId}/fix`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw new Error(body || `Status ${res.status}`);
      }
      setModuleMessage(moduleId, 'Fix completed');
    } catch (err) {
      console.error('Module fix failed', err);
      const msg = err instanceof Error ? err.message : String(err);
      setModuleMessage(moduleId, `Fix failed: ${msg}`);
    }
    setTimeout(() => setModuleMessage(moduleId, ''), 5000);
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
        <TabsList className="flex gap-2 flex-wrap">
          <TabsTrigger value="company">Company</TabsTrigger>
          <TabsTrigger value="localization">Localization</TabsTrigger>
          
          {/* Module-specific settings tabs (for modules that expose `configurables`) */}
          {modules.map((m) => (
            <TabsTrigger key={m.module.id} value={`module:${m.module.id}`}>
              {m.module.name}
            </TabsTrigger>
          ))}
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

        

        {/* Module-specific Tabs (configurables) */}
        {modules.map((m) => {
          const moduleId = m.module.id;
          const cfg = (m.config as unknown as Record<string, unknown>).configurables as unknown;
          const values = editableConfigs[moduleId] || {};

          return (
            <TabsContent key={moduleId} value={`module:${moduleId}`} className="space-y-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                    <CardTitle>{m.module.name} Settings</CardTitle>
                  </div>
                  <CardDescription>
                    Module: {m.module.id} • version {m.module.version}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {modulesLoading && <p className="text-sm text-muted-foreground">Loading...</p>}

                  {!cfg && <p className="text-sm text-muted-foreground">No configurables exposed by this module.</p>}

                  {cfg && Array.isArray(cfg) && (
                    <div className="space-y-4">
                      {(cfg as Array<Record<string, unknown>>).map((item) => {
                        const key = (item['key'] as string) || (item['id'] as string);
                        const label = (item['label'] as string) || key;
                        const type = (item['type'] as string) || 'text';
                        const desc = (item['description'] as string) || (item['help_text'] as string) || '';
                        const val = values[key] as unknown;
                        return (
                          <div key={key}>
                            <Label>{label}</Label>
                            {type === 'boolean' ? (
                              <div className="flex items-center justify-between">
                                <p className="text-sm text-muted-foreground">{desc}</p>
                                <Switch
                                  checked={Boolean(val)}
                                  onCheckedChange={(checked) => {
                                    setEditableConfigs((prev) => ({ ...prev, [moduleId]: { ...(prev[moduleId] || {}), [key]: checked } }));
                                  }}
                                />
                              </div>
                            ) : (
                              <Input
                                value={val ?? ''}
                                onChange={(e) => setEditableConfigs((prev) => ({ ...prev, [moduleId]: { ...(prev[moduleId] || {}), [key]: e.target.value } }))}
                              />
                            )}
                            {desc && <p className="text-xs text-muted-foreground mt-1">{desc}</p>}
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {cfg && !Array.isArray(cfg) && (
                    <div className="space-y-4">
                      {Object.entries(cfg as Record<string, Record<string, unknown>>).map(([k, v]) => {
                        const label = (v && ((v.label as string) || (v.title as string))) || k;
                        const type = (v && (v.type as string)) || 'text';
                        const desc = (v && ((v.description as string) || (v.help_text as string))) || '';
                        const val = values[k] as unknown;
                        return (
                          <div key={k}>
                            <Label>{label}</Label>
                            {type === 'boolean' ? (
                              <div className="flex items-center justify-between">
                                <p className="text-sm text-muted-foreground">{desc}</p>
                                <Switch
                                  checked={Boolean(val)}
                                  onCheckedChange={(checked) => setEditableConfigs((prev) => ({ ...prev, [moduleId]: { ...(prev[moduleId] || {}), [k]: checked } }))}
                                />
                              </div>
                            ) : (
                              <Input
                                value={val ?? ''}
                                onChange={(e) => setEditableConfigs((prev) => ({ ...prev, [moduleId]: { ...(prev[moduleId] || {}), [k]: e.target.value } }))}
                              />
                            )}
                            {desc && <p className="text-xs text-muted-foreground mt-1">{desc}</p>}
                          </div>
                        );
                      })}
                    </div>
                  )}

                  <div className="flex items-center gap-3 mt-4">
                    <Button onClick={() => handleSaveModuleConfigurables(moduleId)}>
                      <Save className="mr-2 h-4 w-4" />
                      Save
                    </Button>
                    <Button variant="outline" onClick={() => handleFixModule(moduleId)}>
                      <AlertTriangle className="mr-2 h-4 w-4" />
                      Fix Module Schema
                    </Button>
                    {moduleMessages[moduleId] && (
                      <span className="text-sm text-muted-foreground">{moduleMessages[moduleId]}</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          );
        })}
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
