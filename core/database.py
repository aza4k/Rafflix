from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import settings

if not settings.ASYNC_DATABASE_URL:
    # During build or initial setup, we might not have a URL yet.
    # We create a dummy engine or handle it gracefully.
    engine = None
    AsyncSessionLocal = None
else:
    engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True
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
    if AsyncSessionLocal is None:
        raise RuntimeError("DATABASE_URL is not set. Please configure it in your environment.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
