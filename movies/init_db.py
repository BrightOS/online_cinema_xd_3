import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from db.models import Base 
from config import Settings

settings = Settings()

async def create_tables():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())
