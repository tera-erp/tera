import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "@/components/layout/MainLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, AlertCircle } from "lucide-react";
import { ModuleConfig } from "@/modules";
import * as LucideIcons from "lucide-react";

const ModulesDashboard: React.FC = () => {
  const navigate = useNavigate();
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

  const getIconComponent = (iconName?: string) => {
    if (!iconName) return null;
    const Icon = (LucideIcons as any)[iconName];
    return Icon ? <Icon className="h-6 w-6" /> : null;
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-96">
          <div className="flex gap-2 items-center">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            <p className="text-muted-foreground">Loading modules...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Modules</h1>
        <p className="mt-1 text-muted-foreground">
          Available modules and features for your ERP system
        </p>
      </div>

      {error && (
        <Card className="mb-6 border-destructive/50 bg-destructive/10">
          <CardContent className="pt-6 flex gap-3">
            <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
            <p className="text-sm text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {modules.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground text-center py-8">No modules available</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {modules.map((module) => (
            <Card key={module.module.id} className="hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-3 flex-1">
                    {module.module.icon && (
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                        {getIconComponent(module.module.icon)}
                      </div>
                    )}
                    <div className="flex-1">
                      <CardTitle className="text-lg">{module.module.name}</CardTitle>
                      <p className="text-xs text-muted-foreground mt-1">v{module.module.version}</p>
                    </div>
                  </div>
                </div>
                <CardDescription className="mt-2">{module.module.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Screens */}
                {module.screens && Object.entries(module.screens).length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Screens</p>
                    <div className="space-y-1">
                      {Object.entries(module.screens)
                        .filter(([_, screen]) => screen.show_in_nav !== false)
                        .map(([screenId, screen]) => (
                          <Button
                            key={screenId}
                            variant="outline"
                            size="sm"
                            className="w-full justify-start text-xs"
                            onClick={() => navigate(screen.path)}
                          >
                            {screen.title}
                          </Button>
                        ))}
                    </div>
                  </div>
                )}

                {/* Workflows */}
                {module.workflows && Object.entries(module.workflows).length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                      Workflows
                    </p>
                    <div className="space-y-1">
                      {Object.entries(module.workflows).map(([wfId, wf]) => (
                        <div key={wfId} className="text-xs text-muted-foreground flex items-center gap-1">
                          <span>•</span>
                          <span>{wf.title}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </MainLayout>
  );
};

export default ModulesDashboard;
