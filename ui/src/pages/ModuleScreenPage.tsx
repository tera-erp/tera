import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import MainLayout from "@/components/layout/MainLayout";
import { FormRenderer, ListRenderer, DetailRenderer } from "@/modules/components";
import { ModuleConfig, ScreenConfig } from "@/modules";
import { ModulePathDebugger, logModuleDebug } from "@/modules/ModulePathDebugger";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle, Loader2 } from "lucide-react";
import { useCompany } from "@/context/CompanyContext";

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
interface ModuleScreenPageProps {}

const ModuleScreenPage: React.FC<ModuleScreenPageProps> = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const { activeCompany } = useCompany();
  const { moduleId } = useParams<{
    moduleId?: string;
  }>();
  const [editMode, setEditMode] = useState(false);
  const [moduleConfig, setModuleConfig] = useState<ModuleConfig | null>(null);
  const [screenConfig, setScreenConfig] = useState<ScreenConfig | null>(null);
  const [derivedScreenId, setDerivedScreenId] = useState<string | null>(null);
  const [derivedRecordId, setDerivedRecordId] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string>("");

  useEffect(() => {
    console.log("ModuleScreenPage mounted with path:", location.pathname);
  }, [location.pathname]);

  const matchScreenPath = (screenPath: string, currentPath: string): { recordId?: string } | null => {
    if (!screenPath) return null;
    
    // Normalize paths: remove trailing slashes for comparison
    const normalizedScreen = screenPath.replace(/\/$/, "");
    const normalizedCurrent = currentPath.replace(/\/$/, "");
    
    // Escape regex chars except our placeholder
    const escaped = normalizedScreen
      .replace(/[-/\\^$+?.()|[\]{}]/g, "\\$&")
      .replace(/\\\{id\\\}/g, "([^/]+)");
    
    const regex = new RegExp(`^${escaped}$`);
    const m = normalizedCurrent.match(regex);
    
    if (!m) return null;
    return { recordId: m[1] || undefined };
  };

  // Fetch module config
  useEffect(() => {
    if (!moduleId) {
      console.error("No moduleId provided");
      return;
    }

    const fetchModule = async () => {
      try {
        console.log("Fetching module:", moduleId);
        const response = await fetch(`/api/v1/modules/${moduleId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        });
        if (!response.ok) {
          console.error("Module fetch failed:", response.status, response.statusText);
          throw new Error("Failed to fetch module");
        }
        const data = await response.json();
        console.log("Module data received:", data);
        setModuleConfig(data);

        // Resolve screen by matching current path to declarative paths in YAML
        const currentPath = location.pathname;
        let foundScreenId: string | null = null;
        let foundRecordId: string | null = null;

        // Debug: log path matching info
        if (process.env.NODE_ENV === "development") {
          logModuleDebug(currentPath, moduleId!, data.screens || {});
        }

        // Validate module config
        const configErrors = ModulePathDebugger.validateModuleConfig(data);
        if (configErrors.length > 0) {
          console.warn("Module config issues:", configErrors);
        }

        for (const [key, screen] of Object.entries(data.screens || {})) {
          if (!screen?.path) continue;
          const match = matchScreenPath(screen.path, currentPath);
          if (match) {
            foundScreenId = key;
            foundRecordId = match.recordId || null;
            setScreenConfig(screen);
            break;
          }
        }

        if (!foundScreenId) {
          const availableScreens = Object.entries(data.screens || {}).map(([key, s]: any) => ({
            key,
            path: s.path,
            type: s.type,
          }));
          console.error("No screen path matched current route:", {
            currentPath,
            availableScreens,
          });
          setLoadError(`Route not found: "${currentPath}". Available paths: ${availableScreens.map(s => s.path).join(", ") || "none"}`);
        }

        setDerivedScreenId(foundScreenId);
        setDerivedRecordId(foundRecordId);
      } catch (err) {
        console.error("Failed to fetch module:", err);
        setLoadError(err instanceof Error ? err.message : "Failed to load module");
      }
    };

    fetchModule();
  }, [moduleId, location.pathname]);

  // Fetch list data
  const {
    data: listData = [],
    isLoading: listLoading,
    error: listError,
  } = useQuery({
    queryKey: [moduleId, derivedScreenId, "list"],
    queryFn: async () => {
      if (!screenConfig?.endpoint || screenConfig.type !== "list") return [];
      console.log("Fetching list data from:", screenConfig.endpoint);
      const response = await fetch(screenConfig.endpoint, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (!response.ok) {
        console.error("List fetch failed:", response.status);
        throw new Error("Failed to fetch data");
      }
      const data = await response.json();
      console.log("List data received:", data);
      return data;
    },
    enabled: !!(screenConfig?.endpoint && screenConfig?.type === "list"),
  });

  // Fetch detail data
  const {
    data: detailData,
    isLoading: detailLoading,
    error: detailError,
  } = useQuery({
    queryKey: [moduleId, derivedScreenId, derivedRecordId],
    queryFn: async () => {
      if (!screenConfig?.endpoint || !derivedRecordId || screenConfig.type !== "detail") {
        return null;
      }
      const endpoint = screenConfig.endpoint.replace("{id}", derivedRecordId);
      console.log("Fetching detail data from:", endpoint);
      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch record");
      return response.json();
    },
    enabled: !!screenConfig?.endpoint && !!derivedRecordId && screenConfig?.type === "detail",
  });

  // Derived flags
  const isCreating = derivedRecordId === "new" || !derivedRecordId;
  const listQueryKey = [moduleId, derivedScreenId, "list"] as const;
  const detailQueryKey = [moduleId, derivedScreenId, derivedRecordId] as const;

  // Edit mutation
  // Determine current workflow state from data
  const currentWorkflowState = detailData?.status || moduleConfig?.workflows?.[Object.keys(moduleConfig.workflows || {})[0]]?.initial_state;
  const currentWorkflow = moduleConfig?.workflows?.[Object.keys(moduleConfig.workflows || {})[0]];
  const canEditBasedOnWorkflow = currentWorkflow ? currentWorkflow.states[currentWorkflowState]?.allow_edit ?? true : true;

  const editMutation = useMutation({
    mutationFn: async (data: any) => {
      if (!derivedRecordId || !screenConfig?.endpoint) throw new Error("No endpoint");
      const endpoint = screenConfig.endpoint.replace("{id}", derivedRecordId);
      const response = await fetch(endpoint, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error("Failed to update record");
      return response.json();
    },
    onSuccess: () => {
      setEditMode(false);
      queryClient.invalidateQueries({ queryKey: detailQueryKey });
      queryClient.invalidateQueries({ queryKey: listQueryKey });
    },
  });

  // Workflow transition mutation
  const transitionMutation = useMutation({
    mutationFn: async (transitionKey: string) => {
      if (!derivedRecordId || !screenConfig?.endpoint) throw new Error("No endpoint");
      
      // Get the transition config
      const transition = currentWorkflow?.transitions?.[transitionKey];
      if (!transition) throw new Error("Transition not found");
      
      // Extract action name (e.g., "payroll.deactivate_employee" -> endpoint)
      // Try common patterns for action endpoints
      const actionMapping: Record<string, string> = {
        deactivate: `/api/v1/employees/${derivedRecordId}/deactivate`,
        reactivate: `/api/v1/employees/${derivedRecordId}/reactivate`,
        terminate: `/api/v1/employees/${derivedRecordId}/terminate`,
        process: `/api/v1/payroll-runs/${derivedRecordId}/process`,
        complete: `/api/v1/payroll-runs/${derivedRecordId}/complete`,
        release_payment: `/api/v1/payroll-runs/${derivedRecordId}/release`,
        revert: `/api/v1/payroll-runs/${derivedRecordId}/revert`,
      };
      
      // Use mapped endpoint or fallback to action name
      const actionName = transition.action.split('.').pop() || transitionKey;
      const endpoint = actionMapping[actionName] || `/api/v1/${moduleId}/${actionName}/${derivedRecordId}`;
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({}),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Transition failed" }));
        throw new Error(errorData.detail || "Transition failed");
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: detailQueryKey });
      queryClient.invalidateQueries({ queryKey: listQueryKey });
    },
  });

  const resolveScreenPath = (screenKey?: string | null, id?: string) => {
    if (!screenKey) return null;
    const scr = moduleConfig?.screens?.[screenKey];
    if (!scr?.path) return null;
    return id ? scr.path.replace("{id}", id) : scr.path;
  };

  const navigateToScreen = (screenKey?: string | null, id?: string) => {
    const path = resolveScreenPath(screenKey, id);
    if (path) navigate(path);
  };

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!derivedRecordId || !screenConfig?.endpoint) throw new Error("No endpoint");
      const endpoint = screenConfig.endpoint.replace("{id}", derivedRecordId);
      const response = await fetch(endpoint, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (!response.ok) throw new Error("Failed to delete record");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: listQueryKey });
      const listPath = screenConfig?.path?.replace(/\/{id}/, "").replace("{id}", "");
      navigate(listPath || `/modules/${moduleId}`);
    },
  });

  // For create mode, setup a create mutation that POSTs instead of PUTs
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      if (!screenConfig?.endpoint) throw new Error("No endpoint");
      const endpoint = screenConfig.endpoint.replace("/{id}/", "").replace("{id}", "").replace(/\/$/, "");
      
      // Inject company_id for employee creation
      const payload = { ...data };
      payload.company_id = activeCompany.id;
      
      const response = await fetch(endpoint + "/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to create record" }));
        throw new Error(errorData.detail || "Failed to create record");
      }
      return response.json();
    },
    onSuccess: (newRecord) => {
      queryClient.invalidateQueries({ queryKey: listQueryKey });
      queryClient.invalidateQueries({ queryKey: detailQueryKey });
      // Navigate to the new record
      // Navigate to the matched screen path with the new id
      navigateToScreen(derivedScreenId, newRecord.id);
    },
  });

  if (loadError) {
    return (
      <MainLayout>
        <Card>
          <CardContent className="pt-6">
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 flex gap-3">
              <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-destructive">Failed to Load Module</p>
                <p className="text-sm text-destructive mt-1">{loadError}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </MainLayout>
    );
  }

  if (!moduleConfig) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-96">
          <div className="flex gap-2 items-center">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            <p className="text-muted-foreground">Loading module... (moduleId: {moduleId})</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (!screenConfig) {
    return (
      <MainLayout>
        <div className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 flex gap-3">
                <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-destructive">Screen Not Found</p>
                  <p className="text-sm text-destructive mt-1">
                    Screen for path "{location.pathname}" not found in module "{moduleId}"
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Available screens: {Object.keys(moduleConfig.screens || {}).join(", ") || "none"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    );
  }

  // Get the form config based on screen type
  let formConfig = null;
  let formName = null;
  if (screenConfig?.type === "detail" && screenConfig?.detail_config?.form) {
    formName = screenConfig.detail_config.form;
    formConfig = moduleConfig?.forms?.[formName];
  } else if (screenConfig?.type === "form") {
    formName = derivedScreenId!;
    formConfig = moduleConfig?.forms?.[derivedScreenId!];
  }

  console.log("Rendering ModuleScreenPage with:", {
    moduleId,
    screenId: derivedScreenId,
    screenType: screenConfig?.type,
    isCreating,
    hasModuleConfig: !!moduleConfig,
    hasScreenConfig: !!screenConfig,
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Render based on screen type */}
        {screenConfig.type === "list" && (
          <ListRenderer
            config={screenConfig}
            data={listData}
            loading={listLoading}
            error={listError instanceof Error ? listError.message : undefined}
            onNew={() => {
              const targetScreen = screenConfig.create_screen || derivedScreenId;
              navigateToScreen(targetScreen, "new");
            }}
            onRow={(record) => navigateToScreen(screenConfig.create_screen || derivedScreenId, record.id)}
          />
        )}

        {screenConfig.type === "detail" && (
          formConfig ? (
            <DetailRenderer
              config={screenConfig}
              formConfig={formConfig}
              recordId={derivedRecordId || "new"}
              data={detailData}
              loading={detailLoading}
              submitLoading={createMutation.isPending || editMutation.isPending}
              deleteLoading={deleteMutation.isPending}
              error={detailError instanceof Error ? detailError.message : undefined}
              isCreating={isCreating}
              onBack={() => {
                const listPath = screenConfig?.path?.replace(/\/{id}/, "").replace("{id}", "");
                navigate(listPath || `/modules/${moduleId}`);
              }}
              onEdit={async (data) => {
                return new Promise<void>((resolve, reject) => {
                  if (isCreating) {
                    createMutation.mutate(data, {
                      onSuccess: () => resolve(),
                      onError: (error) => reject(error),
                    });
                  } else {
                    editMutation.mutate(data, {
                      onSuccess: () => resolve(),
                      onError: (error) => reject(error),
                    });
                  }
                });
              }}
              onDelete={async () => {
                return new Promise<void>((resolve, reject) => {
                  deleteMutation.mutate(undefined, {
                    onSuccess: () => resolve(),
                    onError: (error) => reject(error),
                  });
                });
              }}
              onWorkflowTransition={async (transitionKey: string) => {
                return new Promise<void>((resolve, reject) => {
                  transitionMutation.mutate(transitionKey, {
                    onSuccess: () => resolve(),
                    onError: (error) => reject(error),
                  });
                });
              }}
              editMode={editMode || isCreating}
              onEditModeChange={setEditMode}
              workflow={moduleConfig.workflows?.[Object.keys(moduleConfig.workflows || {})[0]]}
              workflowState={detailData?.status || "draft"}
            />
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="rounded-lg bg-amber-50 border border-amber-200 p-4 flex gap-3">
                  <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0" />
                  <p className="text-sm text-amber-600">
                    Form configuration '{formName}' not found in module forms
                  </p>
                </div>
              </CardContent>
            </Card>
          )
        )}

        {screenConfig.type === "form" && (
          formConfig ? (
            <FormRenderer
              config={formConfig}
              initialData={detailData}
              onSubmit={async (data) => {
                return new Promise<void>((resolve, reject) => {
                  if (isCreating) {
                    createMutation.mutate(data, {
                      onSuccess: () => resolve(),
                      onError: (error) => reject(error),
                    });
                  } else {
                    editMutation.mutate(data, {
                      onSuccess: () => resolve(),
                      onError: (error) => reject(error),
                    });
                  }
                });
              }}
              onCancel={() => {
                const listPath = screenConfig?.path?.replace(/\/{id}/, "").replace("{id}", "");
                navigate(listPath || `/modules/${moduleId}`);
              }}
              loading={createMutation.isPending || editMutation.isPending}
              readOnly={false}
            />
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="rounded-lg bg-amber-50 border border-amber-200 p-4 flex gap-3">
                  <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0" />
                  <p className="text-sm text-amber-600">
                    Form configuration '{formName}' not found in module forms
                  </p>
                </div>
              </CardContent>
            </Card>
          )
        )}

        {!["list", "detail", "form"].includes(screenConfig.type) && (
          <Card>
            <CardContent className="pt-6">
              <div className="rounded-lg bg-amber-50 border border-amber-200 p-4 flex gap-3">
                <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0" />
                <p className="text-sm text-amber-600">
                  Screen type '{screenConfig.type}' is not yet supported
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Debug Info */}
        {process.env.NODE_ENV === 'development' && (
          <Card className="mt-4">
            <CardContent className="pt-6">
              <details className="text-xs">
                <summary className="cursor-pointer font-semibold mb-2">Debug Info</summary>
                <pre className="bg-muted p-2 rounded overflow-auto">
                  {JSON.stringify({
                    moduleId,
                    screenId: derivedScreenId,
                    recordId: derivedRecordId,
                    screenType: screenConfig?.type,
                    hasModuleConfig: !!moduleConfig,
                    hasScreenConfig: !!screenConfig,
                    hasFormConfig: !!formConfig,
                    listLoading,
                    detailLoading,
                    listDataLength: Array.isArray(listData) ? listData.length : 'N/A',
                    listError: listError?.toString(),
                    detailError: detailError?.toString(),
                    path: location.pathname,
                    screenPath: screenConfig?.path,
                  }, null, 2)}
                </pre>
              </details>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  );
};

export default ModuleScreenPage;
