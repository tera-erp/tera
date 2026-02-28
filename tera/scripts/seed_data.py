"""Seed database with initial data for testing."""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from tera.core.database import get_db, engine, Base
from tera.models.company import Company
from tera.modules.finance.models import Partner, Product


async def seed_data():
    """Add initial seed data."""
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Get database session
    async for db in get_db():
        # Check if companies exist
        from sqlalchemy import select
        result = await db.execute(select(Company))
        companies = result.scalars().all()
        
        if not companies:
            print("Creating seed companies...")
            company1 = Company(
                name="Acme Corporation",
                country_code="IDN",
                currency_code="IDR",
                address="Jakarta, Indonesia",
                status="active"
            )
            company2 = Company(
                name="TechStart Pte Ltd",
                country_code="SGP",
                currency_code="SGD",
                address="Singapore",
                status="active"
            )
            company3 = Company(
                name="Global Trade Sdn Bhd",
                country_code="MYS",
                currency_code="MYR",
                address="Kuala Lumpur, Malaysia",
                status="active"
            )
            db.add_all([company1, company2, company3])
            await db.commit()
            print("✓ Created 3 companies")
        else:
            print(f"✓ Found {len(companies)} existing companies")
        
        # Add some customers (partners)
        result = await db.execute(select(Partner))
        partners = result.scalars().all()
        
        if not partners:
            print("Creating seed customers...")
            partner1 = Partner(
                name="ABC Supplies Co",
                country_code="IDN",
                email="contact@abcsupplies.com",
                phone="+62-21-1234567"
            )
            partner2 = Partner(
                name="XYZ Industries",
                country_code="SGP",
                email="info@xyzind.com",
                phone="+65-6123-4567"
            )
            partner3 = Partner(
                name="Global Merchants Ltd",
                country_code="MYS",
                email="sales@globalmerchants.com",
                phone="+60-3-1234567"
            )
            db.add_all([partner1, partner2, partner3])
            await db.commit()
            print("✓ Created 3 customers")
        else:
            print(f"✓ Found {len(partners)} existing customers")
        
        # Add some products
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        if not products:
            print("Creating seed products...")
            product1 = Product(
                name="Software License - Enterprise",
                price=9999.00,
                description="Annual enterprise software license"
            )
            product2 = Product(
                name="Consulting Services (Hourly)",
                price=150.00,
                description="Professional consulting services"
            )
            product3 = Product(
                name="Hardware - Laptop",
                price=1299.00,
                description="Business laptop"
            )
            product4 = Product(
                name="Training Package",
                price=2500.00,
                description="Comprehensive training program"
            )
            db.add_all([product1, product2, product3, product4])
            await db.commit()
            print("✓ Created 4 products")
        else:
            print(f"✓ Found {len(products)} existing products")
        
        print("\n✅ Database seeding complete!")
        break


if __name__ == "__main__":
    asyncio.run(seed_data())
