"""Module setup helpers for the Company module.

Provides a `fix()` function that the modules router can call to ensure
database tables exist for the application. This keeps module initialization
scoped and callable via `/api/v1/modules/company/fix`.
"""
from tera.core.database import engine, Base

async def fix():
    """Create missing tables for the application model metadata.

    This is intentionally generic and will create all tables registered on
    `Base.metadata`. It's safe to call multiple times.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
