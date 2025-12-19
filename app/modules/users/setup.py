"""Module setup helpers for the Users module.

Providing a `fix()` function ensures the DB schema is initialized when
requested via the modules API. This avoids duplicating the user router
logic while allowing the module system to orchestrate fixes.
"""
from app.core.database import engine, Base

async def fix():
    """Ensure database tables exist for application models.

    The implementation is intentionally broad (creates all tables on
    `Base.metadata`) which is safe and idempotent for initialization.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
