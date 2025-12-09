import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import CompanySelector from "@/components/common/CompanySelector";
import { useAuth } from "@/context/AuthContext";
import { ModuleConfig } from "@/modules";
import * as LucideIcons from "lucide-react";
import { 
  LayoutDashboard, 
  Settings, 
  HelpCircle,
  ChevronDown,
  Box,
  Loader2,
} from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

const Sidebar: React.FC = () => {
  const [openModules, setOpenModules] = React.useState<string[]>(["finance"]);
  const [modules, setModules] = useState<ModuleConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();

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
        console.error("Failed to load modules:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchModules();
  }, []);

  const toggleModule = (moduleId: string) => {
    setOpenModules((prev) =>
      prev.includes(moduleId)
        ? prev.filter((id) => id !== moduleId)
        : [...prev, moduleId]
    );
  };

  const getIconComponent = (iconName?: string) => {
    if (!iconName) return Box;
    const Icon = (LucideIcons as any)[iconName];
    return Icon || Box;
  };

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-sidebar text-sidebar-foreground">
      <div className="flex h-full flex-col">
        {/* Company Selector / Logo */}
        <div className="h-16 border-b border-sidebar-border">
          <CompanySelector />
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {/* Dashboard Link */}
          <NavLink
            to="/"
            className={({ isActive }) =>
              cn(
                "mb-2 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/80 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
              )
            }
          >
            <LayoutDashboard className="h-5 w-5" />
            Dashboard
          </NavLink>

          {/* Module Navigation */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2 px-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-sidebar-foreground/50">
                Modules
              </p>
              {loading && <Loader2 className="h-3 w-3 animate-spin text-sidebar-foreground/50" />}
            </div>

            {loading ? (
              <div className="px-3 py-2 text-sm text-sidebar-foreground/50">
                Loading modules...
              </div>
            ) : modules.length === 0 ? (
              <div className="px-3 py-2 text-sm text-sidebar-foreground/50">
                No modules installed
              </div>
            ) : (
              modules.map((module) => {
                const ModuleIcon = getIconComponent(module.module.icon);
                const screens = module.screens 
                  ? Object.entries(module.screens).filter(([_, screen]) => screen.show_in_nav !== false)
                  : [];
                
                return (
                  <Collapsible
                    key={module.module.id}
                    open={openModules.includes(module.module.id)}
                    onOpenChange={() => toggleModule(module.module.id)}
                  >
                    <CollapsibleTrigger className="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-foreground/80 transition-colors hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground">
                      <div className="flex items-center gap-3">
                        <ModuleIcon className="h-5 w-5" />
                        {module.module.name}
                      </div>
                      <ChevronDown
                        className={cn(
                          "h-4 w-4 transition-transform duration-200",
                          openModules.includes(module.module.id) && "rotate-180"
                        )}
                      />
                    </CollapsibleTrigger>
                    <CollapsibleContent className="pl-8">
                      {screens.map(([screenId, screen]) => {
                        const ScreenIcon = getIconComponent(
                          module.menu?.flatMap(m => m.items || [])
                            .find(item => item.path === screen.path)?.icon
                        );
                        
                        return (
                          <NavLink
                            key={screenId}
                            to={`/modules/${module.module.id}/${screenId}`}
                            className={({ isActive }) =>
                              cn(
                                "flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors",
                                isActive
                                  ? "bg-sidebar-primary/10 text-sidebar-primary"
                                  : "text-sidebar-foreground/60 hover:bg-sidebar-accent/30 hover:text-sidebar-foreground"
                              )
                            }
                          >
                            <ScreenIcon className="h-4 w-4" />
                            {screen.title}
                          </NavLink>
                        );
                      })}
                    </CollapsibleContent>
                  </Collapsible>
                );
              })
            )}
          </div>
        </nav>

        {/* Footer */}
        <div className="border-t border-sidebar-border p-3">
          <NavLink
            to="/settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-foreground/80 transition-colors hover:bg-sidebar-accent/50"
          >
            <Settings className="h-5 w-5" />
            Settings
          </NavLink>
          <NavLink
            to="/help"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-foreground/80 transition-colors hover:bg-sidebar-accent/50"
          >
            <HelpCircle className="h-5 w-5" />
            Help & Support
          </NavLink>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
