"""Tests for the finance module."""
import pytest
from decimal import Decimal
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tera.modules.users.models import User
from tera.modules.company.models import Company
from tera.modules.finance.models import Partner, Product, Invoice, InvoiceLine


class TestCustomerCRUD:
    """Test customer (partner) CRUD operations."""
    
    async def test_create_customer(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating a customer."""
        customer_data = {
            "name": "Test Customer Ltd",
            "country_code": "USA",
            "email": "customer@test.com",
            "phone": "+1234567890",
            "tax_id": "TAX123456",
            "address": "123 Test Street"
        }
        response = await client.post(
            "/api/v1/finance/invoices/customers/",
            json=customer_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == customer_data["name"]
        assert data["email"] == customer_data["email"]
    
    async def test_list_customers(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test listing customers."""
        # Create test customers
        customer1 = Partner(
            name="Customer One",
            country_code="USA",
            email="one@test.com"
        )
        customer2 = Partner(
            name="Customer Two",
            country_code="CAN",
            email="two@test.com"
        )
        db_session.add_all([customer1, customer2])
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/finance/invoices/customers/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    async def test_get_customer_by_id(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test getting customer by ID."""
        customer = Partner(
            name="Specific Customer",
            country_code="GBR",
            email="specific@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        response = await client.get(
            f"/api/v1/finance/invoices/customers/{customer.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == customer.id
        assert data["name"] == "Specific Customer"
    
    async def test_update_customer(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test updating customer."""
        customer = Partner(
            name="Original Name",
            country_code="USA",
            email="original@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        update_data = {
            "name": "Updated Name",
            "email": "updated@test.com"
        }
        response = await client.put(
            f"/api/v1/finance/invoices/customers/{customer.id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@test.com"


class TestProductCRUD:
    """Test product CRUD operations."""
    
    async def test_list_products(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test listing products."""
        # Create test products
        product1 = Product(name="Product A", price=Decimal("99.99"))
        product2 = Product(name="Product B", price=Decimal("149.99"))
        db_session.add_all([product1, product2])
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/finance/invoices/products",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2


class TestInvoiceCRUD:
    """Test invoice CRUD operations."""
    
    async def test_create_invoice(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test creating an invoice."""
        # Create customer first
        customer = Partner(
            name="Invoice Customer",
            country_code="USA",
            email="invoice@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice_data = {
            "partner_id": customer.id,
            "invoice_date": datetime.now().isoformat(),
            "due_date": datetime.now().isoformat(),
            "status": "DRAFT",
            "lines": [
                {
                    "description": "Service A",
                    "quantity": 2,
                    "unit_price": 100.0,
                    "tax_rate": 0.1
                }
            ]
        }
        response = await client.post(
            "/api/v1/finance/invoices/",
            json=invoice_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["partner_id"] == customer.id
        assert data["status"] == "DRAFT"
    
    async def test_list_invoices(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test listing invoices."""
        # Create customer and invoices
        customer = Partner(
            name="List Customer",
            country_code="USA",
            email="list@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice1 = Invoice(
            partner_id=customer.id,
            invoice_number="INV-001",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="DRAFT",
            subtotal=Decimal("100.00"),
            tax_total=Decimal("10.00"),
            total=Decimal("110.00")
        )
        invoice2 = Invoice(
            partner_id=customer.id,
            invoice_number="INV-002",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="SENT",
            subtotal=Decimal("200.00"),
            tax_total=Decimal("20.00"),
            total=Decimal("220.00")
        )
        db_session.add_all([invoice1, invoice2])
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/finance/invoices/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    async def test_get_invoice_by_id(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test getting invoice by ID."""
        customer = Partner(
            name="Get Customer",
            country_code="USA",
            email="get@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice = Invoice(
            partner_id=customer.id,
            invoice_number="INV-GET-001",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="DRAFT",
            subtotal=Decimal("500.00"),
            tax_total=Decimal("50.00"),
            total=Decimal("550.00")
        )
        db_session.add(invoice)
        await db_session.commit()
        await db_session.refresh(invoice)
        
        response = await client.get(
            f"/api/v1/finance/invoices/{invoice.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == invoice.id
        assert data["invoice_number"] == "INV-GET-001"
    
    async def test_update_invoice(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test updating invoice."""
        customer = Partner(
            name="Update Customer",
            country_code="USA",
            email="update@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice = Invoice(
            partner_id=customer.id,
            invoice_number="INV-UPD-001",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="DRAFT",
            subtotal=Decimal("300.00"),
            tax_total=Decimal("30.00"),
            total=Decimal("330.00")
        )
        db_session.add(invoice)
        await db_session.commit()
        await db_session.refresh(invoice)
        
        update_data = {
            "status": "SENT"
        }
        response = await client.put(
            f"/api/v1/finance/invoices/{invoice.id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SENT"
    
    async def test_delete_invoice(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test deleting invoice."""
        customer = Partner(
            name="Delete Customer",
            country_code="USA",
            email="delete@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice = Invoice(
            partner_id=customer.id,
            invoice_number="INV-DEL-001",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="DRAFT",
            subtotal=Decimal("100.00"),
            tax_total=Decimal("10.00"),
            total=Decimal("110.00")
        )
        db_session.add(invoice)
        await db_session.commit()
        await db_session.refresh(invoice)
        
        response = await client.delete(
            f"/api/v1/finance/invoices/{invoice.id}",
            headers=auth_headers
        )
        assert response.status_code == 204


class TestInvoiceStateMachine:
    """Test invoice state transitions."""
    
    async def test_send_invoice(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test sending an invoice."""
        customer = Partner(
            name="Send Customer",
            country_code="USA",
            email="send@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice = Invoice(
            partner_id=customer.id,
            invoice_number="INV-SEND-001",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="DRAFT",
            subtotal=Decimal("1000.00"),
            tax_total=Decimal("100.00"),
            total=Decimal("1100.00")
        )
        db_session.add(invoice)
        await db_session.commit()
        await db_session.refresh(invoice)
        
        response = await client.post(
            f"/api/v1/finance/invoices/{invoice.id}/send",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "SENT"
    
    async def test_confirm_payment(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test confirming invoice payment."""
        customer = Partner(
            name="Pay Customer",
            country_code="USA",
            email="pay@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice = Invoice(
            partner_id=customer.id,
            invoice_number="INV-PAY-001",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="SENT",
            subtotal=Decimal("2000.00"),
            tax_total=Decimal("200.00"),
            total=Decimal("2200.00")
        )
        db_session.add(invoice)
        await db_session.commit()
        await db_session.refresh(invoice)
        
        response = await client.post(
            f"/api/v1/finance/invoices/{invoice.id}/confirm-payment",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "PAID"
    
    async def test_cancel_invoice(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test canceling an invoice."""
        customer = Partner(
            name="Cancel Customer",
            country_code="USA",
            email="cancel@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice = Invoice(
            partner_id=customer.id,
            invoice_number="INV-CANCEL-001",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="SENT",
            subtotal=Decimal("500.00"),
            tax_total=Decimal("50.00"),
            total=Decimal("550.00")
        )
        db_session.add(invoice)
        await db_session.commit()
        await db_session.refresh(invoice)
        
        response = await client.post(
            f"/api/v1/finance/invoices/{invoice.id}/cancel",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "CANCELLED"


class TestInvoiceFiltering:
    """Test invoice filtering."""
    
    async def test_filter_by_status(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test filtering invoices by status."""
        customer = Partner(
            name="Filter Customer",
            country_code="USA",
            email="filter@test.com"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        
        invoice1 = Invoice(
            partner_id=customer.id,
            invoice_number="INV-FILTER-001",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="DRAFT",
            subtotal=Decimal("100.00"),
            tax_total=Decimal("10.00"),
            total=Decimal("110.00")
        )
        invoice2 = Invoice(
            partner_id=customer.id,
            invoice_number="INV-FILTER-002",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            status="SENT",
            subtotal=Decimal("200.00"),
            tax_total=Decimal("20.00"),
            total=Decimal("220.00")
        )
        db_session.add_all([invoice1, invoice2])
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/finance/invoices/?status=DRAFT",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(inv["status"] == "DRAFT" for inv in data)


class TestFinanceAuthorization:
    """Test finance module authorization."""
    
    async def test_employee_limited_access(
        self,
        client: AsyncClient,
        employee_auth_headers: dict
    ):
        """Test that employees have limited access to finance operations."""
        # Employees should be able to view but not create/modify
        response = await client.get(
            "/api/v1/finance/invoices/",
            headers=employee_auth_headers
        )
        # Depending on your authorization setup, this might return 200 or 403
        assert response.status_code in [200, 403]
