import React from "react";
import { Link } from "react-router-dom";
import { 
  Plus, 
  Download, 
  RefreshCw,
  Send,
  Beaker,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocalization } from "@/context/LocalizationContext";

const QuickActions: React.FC = () => {
  const { currentLocalization } = useLocalization();

  const actions = [
    {
      label: "Test Features",
      icon: Beaker,
      variant: "default" as const,
      to: "/test-lab",
    },
    {
      label: `${currentLocalization.eInvoice.system}`,
      icon: Send,
      variant: "outline" as const,
      to: "/modules",
    },
    {
      label: "Export Report",
      icon: Download,
      variant: "outline" as const,
    },
  ];

  return (
    <div className="flex flex-wrap gap-3 opacity-0 animate-fade-in stagger-1">
      {actions.map((action) => {
        const buttonContent = (
          <>
            <action.icon className="mr-2 h-4 w-4" />
            {action.label}
          </>
        );

        if (action.to) {
          return (
            <Link key={action.label} to={action.to}>
              <Button
                variant={action.variant}
                className={
                  action.variant === "default"
                    ? "bg-accent hover:bg-accent/90 text-accent-foreground"
                    : "border-border hover:bg-secondary"
                }
              >
                {buttonContent}
              </Button>
            </Link>
          );
        }

        return (
          <Button
            key={action.label}
            variant={action.variant}
            className={
              action.variant === "default"
                ? "bg-accent hover:bg-accent/90 text-accent-foreground"
                : "border-border hover:bg-secondary"
            }
          >
            {buttonContent}
          </Button>
        );
      })}
    </div>
  );
};

export default QuickActions;
