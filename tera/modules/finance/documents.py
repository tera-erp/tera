"""
Document generation helpers for different document types.
Provides specialized formatting and data preparation for various document categories.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from tera.modules.core.document_engine import DocumentData, PartyData, LineItemData


class InvoiceDocumentHelper:
    """Helper for generating invoice documents"""
    
    @staticmethod
    def prepare_document_data(
        invoice_id: int,
        invoice_number: str,
        customer_name: str,
        customer_email: Optional[str],
        customer_phone: Optional[str],
        customer_country: Optional[str],
        invoice_date: datetime,
        currency: str,
        amount_untaxed: float,
        amount_tax: float,
        amount_total: float,
        line_items: List[Dict[str, Any]],
        notes: Optional[str] = None,
    ) -> DocumentData:
        """Prepare invoice data for document generation"""
        parties = {
            "customer": PartyData(
                name=customer_name,
                email=customer_email,
                phone=customer_phone,
                country_code=customer_country,
            )
        }
        
        items = [
            LineItemData(
                description=item.get("product_name", ""),
                quantity=float(item.get("quantity", 1)),
                unit_price=float(item.get("price_unit", 0)),
                amount=float(item.get("amount", 0)),
            )
            for item in line_items
        ]
        
        return DocumentData(
            document_type="invoice",
            document_number=invoice_number,
            date_issued=invoice_date,
            currency=currency,
            amount_total=amount_total,
            notes=notes,
            parties=parties,
            line_items=items,
        )


class PayslipDocumentHelper:
    """Helper for generating payslip documents"""
    
    @staticmethod
    def prepare_document_data(
        payslip_id: int,
        payslip_number: str,
        employee_name: str,
        employee_id: str,
        employee_email: Optional[str],
        employee_phone: Optional[str],
        payroll_date: datetime,
        currency: str,
        gross_salary: float,
        deductions: float,
        net_salary: float,
        salary_components: List[Dict[str, Any]],
        deduction_components: List[Dict[str, Any]],
        notes: Optional[str] = None,
    ) -> DocumentData:
        """Prepare payslip data for document generation"""
        parties = {
            "employee": PartyData(
                name=employee_name,
                email=employee_email,
                phone=employee_phone,
            )
        }
        
        # Combine salary and deduction components
        line_items = []
        
        # Add salary components
        for component in salary_components:
            line_items.append(
                LineItemData(
                    description=f"{component.get('name', '')} (Earning)",
                    quantity=1.0,
                    unit_price=float(component.get("amount", 0)),
                    amount=float(component.get("amount", 0)),
                )
            )
        
        # Add deduction components
        for component in deduction_components:
            line_items.append(
                LineItemData(
                    description=f"{component.get('name', '')} (Deduction)",
                    quantity=1.0,
                    unit_price=-float(component.get("amount", 0)),
                    amount=-float(component.get("amount", 0)),
                )
            )
        
        return DocumentData(
            document_type="payslip",
            document_number=payslip_number,
            date_issued=payroll_date,
            currency=currency,
            amount_total=net_salary,
            notes=notes or f"Gross: {gross_salary:.2f} | Deductions: {deductions:.2f} | Net: {net_salary:.2f}",
            parties=parties,
            line_items=line_items,
        )


class ReportDocumentHelper:
    """Helper for generating generic reports"""
    
    @staticmethod
    def prepare_document_data(
        report_number: str,
        report_title: str,
        report_date: datetime,
        currency: str,
        total_amount: float,
        sections: List[Dict[str, Any]],
        notes: Optional[str] = None,
    ) -> DocumentData:
        """Prepare report data for document generation"""
        line_items = []
        
        # Convert sections to line items
        for section in sections:
            if isinstance(section.get("items"), list):
                for item in section["items"]:
                    line_items.append(
                        LineItemData(
                            description=f"{section.get('title', '')} - {item.get('description', '')}",
                            quantity=float(item.get("quantity", 1)),
                            unit_price=float(item.get("amount", 0)),
                            amount=float(item.get("amount", 0)),
                        )
                    )
        
        return DocumentData(
            document_type="report",
            document_number=report_number,
            date_issued=report_date,
            currency=currency,
            amount_total=total_amount,
            notes=notes,
            parties={},
            line_items=line_items,
        )
