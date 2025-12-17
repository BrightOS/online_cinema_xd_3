import asyncio
from session import get_session
from routes.utils.entry import load_entry_details
from sqlalchemy import text
from elasticsearch import Elasticsearch

async def main():
    es = Elasticsearch("http://localhost:9200")
    async for db in get_session():
        result = await db.execute(text("SELECT id FROM entries"))
        ids = [r[0] for r in result.fetchall()]

        for entry_id in ids:
            details = await load_entry_details(db, entry_id)
            if not details:
                continue
            doc = {
                "id": details.id,
                "status": details.status,
            }
            es.index(index="entries", id=entry_id, body=doc)
            print(f"Indexed: id={details.id}, status={details.status}")

asyncio.run(main())
    