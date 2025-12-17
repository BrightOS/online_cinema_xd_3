import asyncio
import time
import os
import asyncpg
from elasticsearch import Elasticsearch
from session import get_session
from routes.utils.entry import load_entry_details

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")
PG_DSN = os.environ.get("PG_DSN", "postgresql://user:password@cinema_postgres:5432/cinema_db")

def wait_for_es(url, retries=30, sleep=2):
    for i in range(retries):
        try:
            es = Elasticsearch(url)
            
            if es.ping():
                print(f"[sync_worker] Elasticsearch is up on {url}!")

                return es
        except Exception as e:
            print(f"[sync_worker] Elasticsearch not available yet: {e}")

        print(f"[sync_worker] Waiting for elasticsearch... ({i+1}/{retries})")

        time.sleep(sleep)

    raise RuntimeError("Elasticsearch is not available")

es = wait_for_es(ELASTICSEARCH_URL)

async def handle_notify(conn, pid, channel, payload):
    entry_id = int(payload)

    print(f"[sync_worker] Change event for entry_id = {entry_id}")

    async for db in get_session():
        details = await load_entry_details(db, entry_id)

        if not details:
            es.delete(index="entries", id=entry_id, ignore=[404])

            print(f"[sync_worker] Deleted entry {entry_id} from Elasticsearch")

            return

        doc = details.model_dump() if hasattr(details, 'model_dump') else details.dict()
        es.index(index="entries", id=entry_id, body=doc)

        print(f"[sync_worker] Indexed/Updated entry {entry_id} in Elasticsearch")

async def wait_for_pg(dsn, retries=30, sleep=2):
    for i in range(retries):
        try:
            conn = await asyncpg.connect(dsn=dsn)

            print(f"[sync_worker] Postgres is up on {dsn}!")

            return conn
        except Exception as e:
            print(f"[sync_worker] Postgres not available yet: {e}")
            print(f"[sync_worker] Waiting for postgres... ({i+1}/{retries})")

            await asyncio.sleep(sleep)

    raise RuntimeError("Postgres is not available")

async def main():
    conn = await wait_for_pg(PG_DSN)

    await conn.add_listener('entry_changed', handle_notify)

    print("[sync_worker] Listening for Postgres events on 'entry_changed' ...")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await conn.close()

asyncio.run(main()) 
