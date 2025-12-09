import React, { useState } from 'react';
import { useCalculatePayslip } from '@/hooks/usePayroll';
import { useCompany } from '@/context/CompanyContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Users } from 'lucide-react';

const PayrollSimulator = () => {
  const { activeCompany, activeLocalization } = useCompany();
  const { mutate, data, isPending } = useCalculatePayslip();

  const [salary, setSalary] = useState<number>(5000);
  const [age, setAge] = useState<number>(30);
  const [isResident, setIsResident] = useState<boolean>(true);
  const [ptkpStatus, setPtkpStatus] = useState<string>("TK0");

  const handleSimulate = () => {
    mutate({
      country_code: activeCompany.country_code,
      gross_salary: salary,
      age: age,
      is_resident: isResident,
      ptkp_status: activeCompany.country_code === 'ID' ? ptkpStatus : undefined
    });
  };

  return (
    <Card className="w-full max-w-md border-t-4 border-t-purple-500 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5 text-purple-500" />
          Payroll Simulator
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Entity: <span className="font-semibold text-foreground">{activeCompany.name}</span>
          {' · '}
          <span className="text-xs">{activeCompany.country_code}</span>
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="salary">Gross Salary ({activeCompany.currency_code})</Label>
            <Input 
              id="salary"
              type="number" 
              value={salary} 
              onChange={(e) => setSalary(parseFloat(e.target.value) || 0)} 
              min="0"
              step="100"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="age">Employee Age</Label>
            <Input 
              id="age"
              type="number" 
              value={age} 
              onChange={(e) => setAge(parseInt(e.target.value) || 18)} 
              min="18"
              max="70"
            />
          </div>
        </div>

        {activeCompany.country_code === 'SG' && (
          <div className="space-y-2">
            <Label htmlFor="resident">Residency Status</Label>
            <Select value={isResident.toString()} onValueChange={(val) => setIsResident(val === 'true')}>
              <SelectTrigger id="resident">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="true">Singapore PR/Citizen</SelectItem>
                <SelectItem value="false">Foreigner</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        {activeCompany.country_code === 'ID' && (
          <div className="space-y-2">
            <Label htmlFor="ptkp">Tax Status (PTKP)</Label>
            <Select value={ptkpStatus} onValueChange={setPtkpStatus}>
              <SelectTrigger id="ptkp">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="TK0">TK/0 - Single, No Dependents</SelectItem>
                <SelectItem value="K0">K/0 - Married, No Dependents</SelectItem>
                <SelectItem value="K1">K/1 - Married, 1 Dependent</SelectItem>
                <SelectItem value="K2">K/2 - Married, 2 Dependents</SelectItem>
                <SelectItem value="K3">K/3 - Married, 3 Dependents</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        <Button 
          onClick={handleSimulate} 
          disabled={isPending} 
          className="w-full bg-purple-600 hover:bg-purple-700"
        >
          {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Calculate {activeLocalization.name} Payroll
        </Button>

        {data && (
          <div className="mt-4 rounded-lg bg-slate-50 p-4 space-y-3 text-sm border">
             {/* Gross to Net Summary */}
            <div className="grid grid-cols-2 gap-4 text-center mb-4">
                <div className="bg-white p-2 rounded shadow-sm">
                    <div className="text-xs text-muted-foreground">Gross Pay</div>
                    <div className="font-bold">{activeCompany.currency_code} {Number(data.gross_pay).toFixed(2)}</div>
                </div>
                <div className="bg-green-100 p-2 rounded shadow-sm border border-green-200">
                    <div className="text-xs text-green-700">Net Pay</div>
                    <div className="font-bold text-green-800">{activeCompany.currency_code} {Number(data.net_pay).toFixed(2)}</div>
                </div>
            </div>

            {/* Deductions */}
            <div className="space-y-1">
                <p className="text-xs font-semibold text-muted-foreground uppercase">Employee Deductions</p>
                {Object.entries(data.details)
                  .filter(([key]) => key.includes('(Employee)') || key.includes('PPh'))
                  .map(([key, value]) => (
                    <div key={key} className="flex justify-between text-xs">
                        <span>{key}</span>
                        <span className="font-mono text-red-600">-{activeCompany.currency_code} {Number(value).toFixed(2)}</span>
                    </div>
                ))}
            </div>

            {/* Employer Contributions */}
            <div className="space-y-1 pt-2 border-t">
                <p className="text-xs font-semibold text-muted-foreground uppercase">Employer Contributions</p>
                {Object.entries(data.details)
                  .filter(([key]) => key.includes('(Employer)') || (!key.includes('(Employee)') && !key.includes('PPh')))
                  .map(([key, value]) => (
                    <div key={key} className="flex justify-between text-xs">
                        <span>{key}</span>
                        <span className="font-mono text-blue-600">{activeCompany.currency_code} {Number(value).toFixed(2)}</span>
                    </div>
                ))}
            </div>
            
            <div className="pt-2 border-t flex justify-between text-xs font-semibold">
                <span>Total Employer Cost:</span>
                <span>{activeCompany.currency_code} {(Number(data.gross_pay) + Number(data.employer_contribution)).toFixed(2)}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PayrollSimulator;