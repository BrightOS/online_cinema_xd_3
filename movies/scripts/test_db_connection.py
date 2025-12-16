import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings


async def test_connection():
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        async with engine.connect():
            print("Database connection successful!")
            print(f"Connection string: {settings.DATABASE_URL}")
        await engine.dispose()
    except Exception as e:
        print(f"Database connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())
