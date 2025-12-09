import React from "react";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    trend: "up" | "down" | "neutral";
  };
  icon: LucideIcon;
  variant?: "default" | "accent" | "success" | "warning";
  delay?: number;
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  icon: Icon,
  variant = "default",
  delay = 0,
}) => {
  const variantStyles = {
    default: "bg-card border-border",
    accent: "bg-accent/5 border-accent/20",
    success: "bg-success/5 border-success/20",
    warning: "bg-warning/5 border-warning/20",
  };

  const iconStyles = {
    default: "bg-secondary text-muted-foreground",
    accent: "bg-accent/10 text-accent",
    success: "bg-success/10 text-success",
    warning: "bg-warning/10 text-warning",
  };

  const trendColors = {
    up: "text-success",
    down: "text-destructive",
    neutral: "text-muted-foreground",
  };

  return (
    <div
      className={cn(
        "rounded-xl border p-5 shadow-card transition-all duration-300 hover:shadow-elevated opacity-0 animate-slide-up",
        variantStyles[variant]
      )}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="mt-2 text-2xl font-bold text-foreground">{value}</p>
          {change && (
            <p className={cn("mt-1 text-xs font-medium", trendColors[change.trend])}>
              {change.trend === "up" ? "↑" : change.trend === "down" ? "↓" : "→"}{" "}
              {Math.abs(change.value)}% from last month
            </p>
          )}
        </div>
        <div className={cn("rounded-lg p-2.5", iconStyles[variant])}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
