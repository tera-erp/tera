from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Use the validated URI from settings
# echo=True is good for dev (logs SQL), bad for prod
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), 
    echo=settings.DEBUG_MODE
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session