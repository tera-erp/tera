import React from "react";
import { useLocalization } from "@/context/LocalizationContext";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";

const CountrySelector: React.FC = () => {
  const { currentLocalization, setCountry, availableCountries } = useLocalization();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          className="flex items-center gap-2 border-border bg-card hover:bg-secondary"
        >
          <span className="text-lg">{currentLocalization.flag}</span>
          <span className="hidden font-medium sm:inline">{currentLocalization.code}</span>
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Select Region
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {availableCountries.map((country) => (
          <DropdownMenuItem
            key={country.code}
            onClick={() => setCountry(country.code)}
            className={cn(
              "flex items-center justify-between py-2.5",
              currentLocalization.code === country.code && "bg-accent/10"
            )}
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">{country.flag}</span>
              <div>
                <p className="font-medium">{country.name}</p>
                <p className="text-xs text-muted-foreground">
                  {country.currency.code} • {country.eInvoice.system}
                </p>
              </div>
            </div>
            {currentLocalization.code === country.code && (
              <Check className="h-4 w-4 text-accent" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default CountrySelector;
