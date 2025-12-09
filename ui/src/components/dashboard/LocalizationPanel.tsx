import React from "react";
import { useLocalization } from "@/context/LocalizationContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  FileText, 
  Percent, 
  Building2, 
  ExternalLink,
  CheckCircle2,
} from "lucide-react";

const LocalizationPanel: React.FC = () => {
  const { currentLocalization } = useLocalization();

  return (
    <Card className="border-border shadow-card opacity-0 animate-slide-up stagger-3">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3">
            <span className="text-2xl">{currentLocalization.flag}</span>
            <div>
              <h3 className="text-lg font-semibold">{currentLocalization.name} Localization</h3>
              <p className="text-sm font-normal text-muted-foreground">
                {currentLocalization.currency.code} • {currentLocalization.timezone}
              </p>
            </div>
          </CardTitle>
          <Badge variant="outline" className="bg-success/10 text-success border-success/30">
            <CheckCircle2 className="mr-1.5 h-3 w-3" />
            Active
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Tax Rates */}
        <div>
          <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
            <Percent className="h-4 w-4 text-muted-foreground" />
            Tax Configuration
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {currentLocalization.taxes.slice(0, 4).map((tax) => (
              <div
                key={tax.code}
                className="rounded-lg border border-border bg-secondary/30 p-3"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs font-semibold text-muted-foreground">
                    {tax.code}
                  </span>
                  <span className="text-sm font-semibold text-foreground">{tax.rate}%</span>
                </div>
                <p className="text-xs text-muted-foreground truncate">{tax.name}</p>
              </div>
            ))}
          </div>
        </div>

        {/* E-Invoice */}
        <div>
          <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
            <FileText className="h-4 w-4 text-muted-foreground" />
            E-Invoicing System
          </h4>
          <div className="rounded-lg border border-border bg-secondary/30 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-foreground">
                {currentLocalization.eInvoice.system}
              </span>
              {currentLocalization.eInvoice.mandatory && (
                <Badge variant="secondary" className="bg-warning/10 text-warning text-xs">
                  Mandatory
                </Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground mb-2">
              Provider: {currentLocalization.eInvoice.provider}
            </p>
            {currentLocalization.eInvoice.apiEndpoint && (
              <a
                href={currentLocalization.eInvoice.apiEndpoint}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-accent hover:underline"
              >
                <ExternalLink className="h-3 w-3" />
                API Documentation
              </a>
            )}
          </div>
        </div>

        {/* Payroll Funds */}
        <div>
          <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            Statutory Contributions
          </h4>
          <div className="space-y-2">
            {currentLocalization.payroll.slice(0, 3).map((fund) => (
              <div
                key={fund.fund}
                className="flex items-center justify-between rounded-lg border border-border bg-secondary/30 px-3 py-2"
              >
                <span className="text-sm text-foreground">{fund.fund}</span>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-muted-foreground">
                    ER: <span className="font-semibold text-foreground">{fund.employerRate}%</span>
                  </span>
                  <span className="text-muted-foreground">
                    EE: <span className="font-semibold text-foreground">{fund.employeeRate}%</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default LocalizationPanel;
