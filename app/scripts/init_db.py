"""
Database initialization script

This script creates all database tables.
No mock data is seeded - users must create admin account and companies via the web interface.
Run with: python -m app.scripts.init_db
"""
import asyncio
from app.core.database import engine, Base
from app.models import User, Company, EmployeeProfile  # Import all models


async def init_db():
    """Create all database tables"""
    print("Creating database tables...")
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
