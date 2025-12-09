import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  FileText, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  ArrowRight,
} from "lucide-react";
import { useLocalization } from "@/context/LocalizationContext";
import { cn } from "@/lib/utils";

interface ActivityItem {
  id: string;
  type: "invoice" | "payment" | "submission";
  title: string;
  description: string;
  status: "success" | "pending" | "error";
  timestamp: Date;
  amount?: number;
}

const RecentActivity: React.FC = () => {
  const { formatCurrency, formatDate, currentLocalization } = useLocalization();

  // Sample data - would come from API
  const activities: ActivityItem[] = [
    {
      id: "1",
      type: "submission",
      title: `${currentLocalization.eInvoice.system} Submitted`,
      description: "INV-2024-0156 validated successfully",
      status: "success",
      timestamp: new Date(),
      amount: 15000,
    },
    {
      id: "2",
      type: "invoice",
      title: "Invoice Created",
      description: "INV-2024-0157 for PT. Example Corp",
      status: "pending",
      timestamp: new Date(Date.now() - 3600000),
      amount: 25000,
    },
    {
      id: "3",
      type: "payment",
      title: "Payment Received",
      description: "From SG Holdings Pte Ltd",
      status: "success",
      timestamp: new Date(Date.now() - 7200000),
      amount: 50000,
    },
    {
      id: "4",
      type: "submission",
      title: `${currentLocalization.eInvoice.system} Failed`,
      description: "INV-2024-0155 - Invalid NPWP format",
      status: "error",
      timestamp: new Date(Date.now() - 10800000),
    },
  ];

  const statusIcons = {
    success: CheckCircle2,
    pending: Clock,
    error: AlertCircle,
  };

  const statusStyles = {
    success: "text-success bg-success/10",
    pending: "text-warning bg-warning/10",
    error: "text-destructive bg-destructive/10",
  };

  return (
    <Card className="border-border shadow-card opacity-0 animate-slide-up stagger-4">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-lg font-semibold">Recent Activity</CardTitle>
        <button className="inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline">
          View All
          <ArrowRight className="h-4 w-4" />
        </button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => {
            const StatusIcon = statusIcons[activity.status];
            return (
              <div
                key={activity.id}
                className="flex items-start gap-4 rounded-lg border border-border/50 bg-secondary/20 p-4 transition-colors hover:bg-secondary/40"
              >
                <div className={cn("rounded-lg p-2", statusStyles[activity.status])}>
                  <StatusIcon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-medium text-foreground truncate">{activity.title}</p>
                    {activity.amount && (
                      <span className="text-sm font-semibold text-foreground whitespace-nowrap">
                        {formatCurrency(activity.amount)}
                      </span>
                    )}
                  </div>
                  <p className="mt-0.5 text-sm text-muted-foreground truncate">
                    {activity.description}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {formatDate(activity.timestamp)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default RecentActivity;
