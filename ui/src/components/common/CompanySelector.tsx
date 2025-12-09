import React from "react";
import { useCompany } from "@/context/CompanyContext";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, Check, Building2, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const CompanySelector: React.FC = () => {
  const { activeCompany, availableCompanies, switchCompany } = useCompany();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          className="h-auto flex items-center gap-3 px-3 py-2 hover:bg-sidebar-accent/50 w-full justify-start"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sidebar-primary flex-shrink-0">
            <Building2 className="h-5 w-5 text-sidebar-primary-foreground" />
          </div>
          <div className="flex-1 text-left">
            <div className="flex items-center gap-2">
              <h1 className="text-base font-semibold text-sidebar-accent-foreground">
                {activeCompany.name.split(' ')[0]}
              </h1>
              <span className="text-xs px-1.5 py-0.5 rounded bg-sidebar-accent/20 text-sidebar-accent-foreground font-medium">
                {activeCompany.country_code}
              </span>
            </div>
            <p className="text-xs text-sidebar-foreground/60">Enterprise Suite</p>
          </div>
          <ChevronDown className="h-4 w-4 text-sidebar-foreground/60 flex-shrink-0" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-80" side="right">
        <DropdownMenuLabel className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Switch Company
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {availableCompanies.map((company) => (
          <DropdownMenuItem
            key={company.id}
            onClick={() => switchCompany(company.id)}
            className={cn(
              "flex items-center justify-between py-3 cursor-pointer",
              activeCompany.id === company.id && "bg-accent/10"
            )}
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Building2 className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">{company.name}</p>
                <p className="text-xs text-muted-foreground">
                  {company.country_code} • {company.currency_code}
                </p>
              </div>
            </div>
            {activeCompany.id === company.id && (
              <Check className="h-4 w-4 text-accent" />
            )}
          </DropdownMenuItem>
        ))}
        <DropdownMenuSeparator />
        <DropdownMenuItem className="flex items-center gap-2 py-2.5 text-muted-foreground">
          <Settings className="h-4 w-4" />
          System Settings
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default CompanySelector;
