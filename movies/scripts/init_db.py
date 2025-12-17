import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from db.models import Base
from config import settings

async def init_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION notify_entry_change_main() RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify('entry_changed', COALESCE(NEW.id, OLD.id)::text);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """))

        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION notify_entry_change_related() RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify('entry_changed', COALESCE(NEW.entry_id, OLD.entry_id)::text);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """))

        await conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_trigger WHERE tgname = 'entry_changed_trg'
            ) THEN
                CREATE TRIGGER entry_changed_trg
                AFTER INSERT OR UPDATE OR DELETE ON entries
                FOR EACH ROW EXECUTE FUNCTION notify_entry_change_main();
            END IF;
        END $$;
        """))

        related_tables = [
            "entry_locales",
            "entry_staff",
            "entry_genres",
            "episodes",
            "episode_locales",
            "franchise_locales",
        ]

        for tname in related_tables:
            await conn.execute(text(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = '{tname}_changed_trg'
                ) THEN
                    CREATE TRIGGER {tname}_changed_trg
                    AFTER INSERT OR UPDATE OR DELETE ON {tname}
                    FOR EACH ROW EXECUTE FUNCTION notify_entry_change_related();
                END IF;
            END $$;
            """))

    await engine.dispose()
    print("Database initialized successfully!")

asyncio.run(init_db())
