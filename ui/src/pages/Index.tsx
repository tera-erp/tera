import React, { useEffect, useState } from "react";
import MainLayout from "@/components/layout/MainLayout";
import ModuleCard from "@/components/dashboard/ModuleCard";
import LocalizationPanel from "@/components/dashboard/LocalizationPanel";
import StatsCard from "@/components/dashboard/StatsCard";
import QuickActions from "@/components/dashboard/QuickActions";
import RecentActivity from "@/components/dashboard/RecentActivity";
import { useLocalization } from "@/context/LocalizationContext";
import { 
  FileText, 
  CreditCard, 
  AlertTriangle, 
  TrendingUp,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { ModuleConfig } from "@/modules";

const Index: React.FC = () => {
  const { formatCurrency, currentLocalization } = useLocalization();
  const [modules, setModules] = useState<ModuleConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchModules = async () => {
      try {
        const response = await fetch("/api/v1/modules/", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        });
        if (!response.ok) throw new Error("Failed to fetch modules");
        const data = await response.json();
        setModules(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load modules");
      } finally {
        setLoading(false);
      }
    };

    fetchModules();
  }, []);

  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2 opacity-0 animate-fade-in">
          <span className="text-lg">{currentLocalization.flag}</span>
          <span>{currentLocalization.name} Operations</span>
          <span className="text-muted-foreground/50">•</span>
          <span>{currentLocalization.currency.code}</span>
        </div>
        <h1 className="text-3xl font-bold text-foreground opacity-0 animate-slide-up">
          Dashboard
        </h1>
        <p className="mt-1 text-muted-foreground opacity-0 animate-slide-up stagger-1">
          Welcome back. Here's an overview of your {currentLocalization.name} operations.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <QuickActions />
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Revenue"
          value={formatCurrency(2450000)}
          change={{ value: 12.5, trend: "up" }}
          icon={TrendingUp}
          variant="accent"
          delay={100}
        />
        <StatsCard
          title="Outstanding Invoices"
          value={formatCurrency(450000)}
          change={{ value: 3.2, trend: "down" }}
          icon={FileText}
          delay={150}
        />
        <StatsCard
          title="Pending Payments"
          value="23"
          change={{ value: 5, trend: "up" }}
          icon={CreditCard}
          variant="warning"
          delay={200}
        />
        <StatsCard
          title={`${currentLocalization.eInvoice.system} Pending`}
          value="5"
          change={{ value: 2, trend: "neutral" }}
          icon={AlertTriangle}
          delay={250}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Modules */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <h2 className="mb-4 text-lg font-semibold text-foreground opacity-0 animate-fade-in stagger-2">
              Active Modules
            </h2>
            {loading ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Loading modules...</span>
              </div>
            ) : error ? (
              <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive flex gap-2 items-center">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            ) : modules.length === 0 ? (
              <p className="text-muted-foreground">No modules available</p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {modules.map((module, index) => (
                  <ModuleCard 
                    key={module.module.id} 
                    module={module} 
                    delay={300 + index * 100}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Recent Activity */}
          <RecentActivity />
        </div>

        {/* Right Column - Localization */}
        <div className="space-y-6">
          <LocalizationPanel />
        </div>
      </div>
    </MainLayout>
  );
};

export default Index;
