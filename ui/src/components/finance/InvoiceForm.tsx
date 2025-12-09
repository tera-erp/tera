import React, { useState } from 'react';
import { useCalculateInvoice } from '@/hooks/useFinance';
import { useCompany } from '@/context/CompanyContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, FileText, CheckCircle2, XCircle } from 'lucide-react';

const InvoiceForm = () => {
  const { activeCompany, activeLocalization } = useCompany(); 
  const { mutate, data, isPending } = useCalculateInvoice();
  
  const [productName, setProductName] = useState<string>("Consulting Service");
  const [quantity, setQuantity] = useState<number>(1);
  const [priceUnit, setPriceUnit] = useState<number>(1000);

  const handleCalculate = () => {
    mutate({
      partner_id: 1, 
      country_code: activeCompany.country_code,
      lines: [
        { product_name: productName, quantity, price_unit: priceUnit }
      ]
    });
  };

  return (
    <Card className="w-full max-w-md border-t-4 border-t-blue-500 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-500" />
          Invoice Calculator
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Entity: <span className="font-semibold text-foreground">{activeCompany.name}</span>
          {' · '}
          <span className="text-xs">{activeCompany.country_code}</span>
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="product">Product/Service</Label>
          <Input 
            id="product"
            value={productName} 
            onChange={(e) => setProductName(e.target.value)}
            placeholder="Description"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity</Label>
            <Input 
              id="quantity"
              type="number" 
              value={quantity} 
              onChange={(e) => setQuantity(parseFloat(e.target.value) || 1)}
              min="1"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="price">Unit Price ({activeCompany.currency_code})</Label>
            <Input 
              id="price"
              type="number" 
              value={priceUnit} 
              onChange={(e) => setPriceUnit(parseFloat(e.target.value) || 0)}
              min="0"
              step="0.01"
            />
          </div>
        </div>
        
        <Button 
          onClick={handleCalculate} 
          disabled={isPending} 
          className="w-full bg-blue-600 hover:bg-blue-700"
        >
          {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Calculate Tax ({activeLocalization.eInvoice.system})
        </Button>

        {data && (
          <div className="mt-4 rounded-lg bg-slate-50 p-4 space-y-3 border">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Subtotal:</span>
              <span className="font-mono">{activeCompany.currency_code} {data.subtotal.toFixed(2)}</span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">{data.tax_name}:</span>
              <span className="font-mono">{activeCompany.currency_code} {data.tax_amount.toFixed(2)}</span>
            </div>

            <div className="pt-2 border-t flex justify-between font-semibold">
              <span>Total:</span>
              <span className="text-lg">{activeCompany.currency_code} {data.total.toFixed(2)}</span>
            </div>

            <div className="pt-2 border-t flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Compliance Check:</span>
              {data.compliance_check ? (
                <span className="flex items-center gap-1 text-green-600">
                  <CheckCircle2 className="h-4 w-4" />
                  Passed
                </span>
              ) : (
                <span className="flex items-center gap-1 text-red-600">
                  <XCircle className="h-4 w-4" />
                  Failed
                </span>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default InvoiceForm;