import React from "react";
import { Link } from "react-router-dom";
import { ModuleConfig } from "@/modules";
import { cn } from "@/lib/utils";
import { ArrowRight } from "lucide-react";
import * as LucideIcons from "lucide-react";

interface ModuleCardProps {
  module: ModuleConfig;
  delay?: number;
}

const ModuleCard: React.FC<ModuleCardProps> = ({ module, delay = 0 }) => {
  const colorMap: Record<string, string> = {
    "module-finance": "from-info/20 to-info/5 hover:from-info/30",
    "module-inventory": "from-success/20 to-success/5 hover:from-success/30",
    "module-hr": "from-purple-500/20 to-purple-500/5 hover:from-purple-500/30",
    "module-localization": "from-warning/20 to-warning/5 hover:from-warning/30",
  };

  const iconColorMap: Record<string, string> = {
    "module-finance": "text-info bg-info/20",
    "module-inventory": "text-success bg-success/20",
    "module-hr": "text-purple-500 bg-purple-500/20",
    "module-localization": "text-warning bg-warning/20",
  };

  const IconComponent = module.module.icon
    ? (LucideIcons as any)[module.module.icon]
    : null;

  const screenEntries = Object.entries(module.screens || {}).filter(
    ([_, screen]) => screen.show_in_nav !== false
  );

  const colorClass = colorMap[module.module.color || ""] || "from-muted/10 to-muted/5 hover:from-muted/20";
  const iconColorClass = iconColorMap[module.module.color || ""] || "text-muted-foreground bg-muted";

  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-xl border border-border bg-gradient-to-br p-6 shadow-card transition-all duration-300 hover:shadow-elevated hover:-translate-y-1 opacity-0 animate-slide-up",
        colorClass
      )}
      style={{ animationDelay: `${delay}ms` }}
    >

      {/* Icon */}
      <div
        className={cn(
          "mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl",
          iconColorClass
        )}
      >
        {IconComponent ? <IconComponent className="h-6 w-6" /> : null}
      </div>

      {/* Content */}
      <h3 className="mb-2 text-lg font-semibold text-foreground">{module.module.name}</h3>
      <p className="mb-4 text-sm text-muted-foreground leading-relaxed">{module.module.description}</p>

      {/* Screens */}
      {screenEntries.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {screenEntries.slice(0, 4).map(([screenId, screen]) => (
            <Link
              key={screenId}
              to={`/modules/${module.module.id}/${screenId}`}
              className="rounded-full px-2.5 py-1 text-xs font-medium transition-all hover:scale-105 bg-background/80 text-foreground/80 hover:bg-background"
            >
              {screen.title}
            </Link>
          ))}
          {screenEntries.length > 4 && (
            <span className="rounded-full bg-background/80 px-2.5 py-1 text-xs font-medium text-muted-foreground">
              +{screenEntries.length - 4} more
            </span>
          )}
        </div>
      )}

      {/* Link */}
      {(() => {
        const firstScreenId = screenEntries[0]?.[0];
        const target = firstScreenId
          ? `/modules/${module.module.id}/${firstScreenId}`
          : "/modules";
        return (
          <Link
            to={target}
            className="inline-flex items-center gap-2 text-sm font-medium text-foreground transition-colors group-hover:text-accent"
          >
            Open Module
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
        );
      })()}
    </div>
  );
};

export default ModuleCard;
