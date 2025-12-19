"""
Database initialization script

This script creates all database tables dynamically from Base.metadata.
All models are auto-discovered by importing app/modules/core/models which
recursively imports all module model files.

Run with: python -m tera.scripts.init_db
"""
import asyncio
from tera.core.database import engine, Base
# Import all models to register them with Base.metadata
# app/modules/core/models.py imports all module-specific models
from tera.modules.core.models import (  # noqa: F401
    ModuleSetting,
    Company,
    User,
    EmployeeProfile,
)
from tera.modules.finance.models import Partner, Invoice, InvoiceLine, Product  # noqa: F401
from tera.modules.payroll.models import PayrollRun, Payslip  # noqa: F401


async def init_db():
    """Create all database tables from Base.metadata"""
    print("Discovering registered models from Base.metadata...")
    # List all tables that will be created
    table_names = sorted(Base.metadata.tables.keys())
    for table_name in table_names:
        print(f"  - {table_name}")

    print(f"\nCreating {len(table_names)} database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created successfully!")
    print("✓ No seed data created - create admin account via the web interface")


async def main():
    """Main initialization function"""
    print("=" * 60)
    print("Tera ERP - Database Initialization")
    print("=" * 60)

    # Create tables
    await init_db()

    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("Ready to create admin account via web interface at /setup")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
