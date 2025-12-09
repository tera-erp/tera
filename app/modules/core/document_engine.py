"""
Universal Document Engine

Generates various document formats (PDF, HTML, JSON, XML) for any document type.
Supports invoices, payroll slips, reports, and custom templates.
"""
from datetime import datetime
from typing import Optional, Dict, List, Union
from enum import Enum
from pydantic import BaseModel
import json
from io import BytesIO


class DocumentFormat(str, Enum):
    """Supported document formats"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    XML = "xml"


class LineItemData(BaseModel):
    """Generic line item data"""
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    amount: float = 0.0
    
    class Config:
        extra = "allow"  # Allow additional fields per document type


class PartyData(BaseModel):
    """Generic party data (customer, vendor, employee, etc.)"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country_code: Optional[str] = None
    tax_id: Optional[str] = None
    
    class Config:
        extra = "allow"


class DocumentData(BaseModel):
    """Base document data structure"""
    document_type: str  # "invoice", "payroll_slip", "report", etc.
    document_number: str
    date_issued: datetime
    currency: str = "USD"
    amount_total: float = 0.0
    notes: Optional[str] = None
    parties: Dict[str, PartyData]  # "customer", "vendor", "employee", etc.
    line_items: List[LineItemData] = []
    
    class Config:
        extra = "allow"  # Allow document-specific fields


class DocumentEngine:
    """Universal document generation engine"""

    @staticmethod
    def generate(
        document_data: DocumentData,
        format: DocumentFormat = DocumentFormat.PDF,
        template: Optional[str] = None,
        locale: str = "en_US"
    ) -> Union[bytes, str]:
        """
        Generate document in specified format.
        
        Args:
            document_data: Complete document data
            format: Output format (PDF, HTML, JSON, XML)
            template: Custom template name (optional)
            locale: Locale for formatting (e.g., en_US, id_ID)
        
        Returns:
            Document content as bytes (PDF) or string (HTML, JSON, XML)
        """
        if format == DocumentFormat.PDF:
            return DocumentEngine._generate_pdf(document_data, template, locale)
        elif format == DocumentFormat.HTML:
            return DocumentEngine._generate_html(document_data, template, locale)
        elif format == DocumentFormat.JSON:
            return DocumentEngine._generate_json(document_data)
        elif format == DocumentFormat.XML:
            return DocumentEngine._generate_xml(document_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _generate_pdf(
        data: DocumentData,
        template: Optional[str] = None,
        locale: str = "en_US"
    ) -> bytes:
        """Generate PDF document"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.enums import TA_CENTER
        except ImportError as e:
            raise ImportError("reportlab is required for PDF generation. Install it with: pip install reportlab") from e

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=12,
        )

        # Title
        doc_title = data.document_type.replace('_', ' ').title()
        story.append(Paragraph(f"{doc_title}", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Document info
        info_data = [
            ['Document Number:', data.document_number],
            ['Date:', data.date_issued.strftime('%Y-%m-%d')],
            ['Currency:', data.currency],
        ]
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))

        # Parties section
        if data.parties:
            story.append(Paragraph("Parties", heading_style))
            for party_type, party_data in data.parties.items():
                party_title = party_type.replace('_', ' ').title()
                party_info = [
                    f"<b>{party_title}</b>",
                    f"Name: {party_data.name}",
                ]
                if party_data.email:
                    party_info.append(f"Email: {party_data.email}")
                if party_data.phone:
                    party_info.append(f"Phone: {party_data.phone}")
                if party_data.address:
                    party_info.append(f"Address: {party_data.address}")
                
                story.append(Paragraph("<br/>".join(party_info), styles['Normal']))
                story.append(Spacer(1, 0.15*inch))

        # Line items
        if data.line_items:
            story.append(Paragraph("Items", heading_style))
            line_table_data = [['Description', 'Quantity', 'Unit Price', 'Amount']]
            for item in data.line_items:
                line_table_data.append([
                    item.description,
                    f"{item.quantity:.2f}",
                    f"{item.unit_price:.2f}",
                    f"{item.amount:.2f}",
                ])
            
            line_table = Table(line_table_data, colWidths=[2.5*inch, 1*inch, 1.25*inch, 1.25*inch])
            line_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            story.append(line_table)

        # Total
        story.append(Spacer(1, 0.2*inch))
        total_data = [
            ['Total Amount:', f"{data.amount_total:.2f} {data.currency}"]
        ]
        total_table = Table(total_data, colWidths=[4.5*inch, 1.5*inch])
        total_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ]))
        story.append(total_table)

        # Notes
        if data.notes:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Notes", heading_style))
            story.append(Paragraph(data.notes, styles['Normal']))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def _generate_html(
        data: DocumentData,
        template: Optional[str] = None,
        locale: str = "en_US"
    ) -> str:
        """Generate HTML document"""
        doc_title = data.document_type.replace('_', ' ').title()
        
        html = f"""<!DOCTYPE html>
<html lang="{locale.split('_')[0]}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_title} - {data.document_number}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            color: #1f2937;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f9fafb;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #1f2937;
            margin-bottom: 30px;
            font-size: 28px;
        }}
        h2 {{
            color: #4b5563;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }}
        .info-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .info-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .info-label {{
            font-weight: 600;
            color: #4b5563;
        }}
        .party {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9fafb;
            border-radius: 4px;
        }}
        .party-type {{
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
        }}
        .party-detail {{
            font-size: 14px;
            color: #6b7280;
            margin: 4px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #e5e7eb;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #1f2937;
            border-bottom: 2px solid #d1d5db;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        .amount {{
            text-align: right;
            font-family: 'Courier New', monospace;
        }}
        .total-section {{
            display: flex;
            justify-content: flex-end;
            margin-top: 30px;
        }}
        .total-row {{
            display: flex;
            justify-content: space-between;
            width: 300px;
            padding: 12px;
            background-color: #f0f0f0;
            border-radius: 4px;
            font-weight: 600;
        }}
        .notes {{
            margin-top: 30px;
            padding: 15px;
            background-color: #f0f9ff;
            border-left: 4px solid #0ea5e9;
            border-radius: 4px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{doc_title}</h1>
        
        <div class="info-section">
            <div>
                <div class="info-item">
                    <span class="info-label">Document Number:</span>
                    <span>{data.document_number}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Date Issued:</span>
                    <span>{data.date_issued.strftime('%Y-%m-%d')}</span>
                </div>
            </div>
            <div>
                <div class="info-item">
                    <span class="info-label">Currency:</span>
                    <span>{data.currency}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Amount:</span>
                    <span class="amount">{data.amount_total:.2f}</span>
                </div>
            </div>
        </div>
"""

        # Parties section
        if data.parties:
            html += "<h2>Parties</h2>\n"
            for party_type, party_data in data.parties.items():
                party_title = party_type.replace('_', ' ').title()
                html += f"""        <div class="party">
            <div class="party-type">{party_title}</div>
            <div class="party-detail">Name: {party_data.name}</div>
"""
                if party_data.email:
                    html += f'            <div class="party-detail">Email: {party_data.email}</div>\n'
                if party_data.phone:
                    html += f'            <div class="party-detail">Phone: {party_data.phone}</div>\n'
                if party_data.address:
                    html += f'            <div class="party-detail">Address: {party_data.address}</div>\n'
                html += "        </div>\n"

        # Line items
        if data.line_items:
            html += """        <h2>Items</h2>
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th class="amount">Quantity</th>
                    <th class="amount">Unit Price</th>
                    <th class="amount">Amount</th>
                </tr>
            </thead>
            <tbody>
"""
            for item in data.line_items:
                html += f"""                <tr>
                    <td>{item.description}</td>
                    <td class="amount">{item.quantity:.2f}</td>
                    <td class="amount">{item.unit_price:.2f}</td>
                    <td class="amount">{item.amount:.2f}</td>
                </tr>
"""
            html += """            </tbody>
        </table>
"""

        # Notes
        if data.notes:
            html += f"""        <div class="notes">
            <h2>Notes</h2>
            <p>{data.notes}</p>
        </div>
"""

        html += """    </div>
</body>
</html>
"""
        return html

    @staticmethod
    def _generate_json(data: DocumentData) -> str:
        """Generate JSON document"""
        doc_dict = {
            "document_type": data.document_type,
            "document_number": data.document_number,
            "date_issued": data.date_issued.isoformat(),
            "currency": data.currency,
            "amount_total": data.amount_total,
            "notes": data.notes,
            "parties": {
                party_type: party_data.dict() 
                for party_type, party_data in data.parties.items()
            },
            "line_items": [item.dict() for item in data.line_items],
        }
        
        # Add any extra fields
        if hasattr(data, '__fields_set__'):
            for field_name in data.__fields_set__:
                if field_name not in doc_dict and field_name not in ['document_type', 'document_number', 'date_issued', 'currency', 'amount_total', 'notes', 'parties', 'line_items']:
                    doc_dict[field_name] = getattr(data, field_name)
        
        return json.dumps(doc_dict, indent=2, default=str)

    @staticmethod
    def _generate_xml(data: DocumentData) -> str:
        """Generate XML document"""
        def _escape_xml(text: str) -> str:
            """Escape special XML characters"""
            if text is None:
                return ""
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&apos;'))

        doc_type = data.document_type.replace('_', '-')
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<{doc_type}>
    <document-number>{_escape_xml(data.document_number)}</document-number>
    <date-issued>{data.date_issued.isoformat()}</date-issued>
    <currency>{_escape_xml(data.currency)}</currency>
    <amount-total>{data.amount_total:.2f}</amount-total>
"""

        if data.notes:
            xml += f"    <notes>{_escape_xml(data.notes)}</notes>\n"

        # Parties
        if data.parties:
            xml += "    <parties>\n"
            for party_type, party_data in data.parties.items():
                party_type_xml = party_type.replace('_', '-')
                xml += f"        <{party_type_xml}>\n"
                xml += f"            <name>{_escape_xml(party_data.name)}</name>\n"
                if party_data.email:
                    xml += f"            <email>{_escape_xml(party_data.email)}</email>\n"
                if party_data.phone:
                    xml += f"            <phone>{_escape_xml(party_data.phone)}</phone>\n"
                if party_data.address:
                    xml += f"            <address>{_escape_xml(party_data.address)}</address>\n"
                if party_data.country_code:
                    xml += f"            <country-code>{_escape_xml(party_data.country_code)}</country-code>\n"
                if party_data.tax_id:
                    xml += f"            <tax-id>{_escape_xml(party_data.tax_id)}</tax-id>\n"
                xml += f"        </{party_type_xml}>\n"
            xml += "    </parties>\n"

        # Line items
        if data.line_items:
            xml += "    <line-items>\n"
            for item in data.line_items:
                xml += """        <item>
            <description>{}</description>
            <quantity>{:.2f}</quantity>
            <unit-price>{:.2f}</unit-price>
            <amount>{:.2f}</amount>
        </item>
""".format(
                    _escape_xml(item.description),
                    item.quantity,
                    item.unit_price,
                    item.amount,
                )
            xml += "    </line-items>\n"

        xml += f"</{doc_type}>\n"
        return xml
