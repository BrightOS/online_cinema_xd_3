import asyncio
import time
import os
import asyncpg
from opentelemetry import trace
from elasticsearch import Elasticsearch
from session import get_session
from routes.utils.entry import load_entry_details

from prometheus_client import start_http_server, Counter
from logger import logger, setup_logging
from tracing import setup_tracing

setup_logging()
setup_tracing(service_name="cinema_etl_worker")

# Metrics
EVENTS_PROCESSED = Counter('etl_events_processed_total', 'Total number of events processed by ETL worker')
SYNC_ERRORS = Counter('etl_sync_errors_total', 'Total number of errors during sync')

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")
PG_DSN = os.environ.get("PG_DSN", "postgresql://user:password@cinema_postgres:5432/cinema_db")

# Start Prometheus metrics server
start_http_server(8001)
logger.info("Prometheus metrics server started on port 8001")

def wait_for_es(url, retries=30, sleep=2):
    for i in range(retries):
        try:
            es = Elasticsearch(url)
            
            if es.ping():
                logger.info(f"Elasticsearch is up on {url}!")

                return es
        except Exception as e:
            logger.error(f"Elasticsearch not available yet: {e}")

        logger.warning(f"Waiting for elasticsearch... ({i+1}/{retries})")

        time.sleep(sleep)

    raise RuntimeError("Elasticsearch is not available")

es = wait_for_es(ELASTICSEARCH_URL)

async def handle_notify(conn, pid, channel, payload):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("handle_pg_notify") as span:
        entry_id = int(payload)
        span.set_attribute("entry_id", entry_id)

        logger.info(f"Change event for entry_id = {entry_id}")

        async for db in get_session():
            details = await load_entry_details(db, entry_id)

            if not details:
                es.delete(index="entries", id=entry_id, ignore=[404])

                logger.info(f"Deleted entry {entry_id} from Elasticsearch")
                EVENTS_PROCESSED.inc()

                return

            doc = details.model_dump() if hasattr(details, 'model_dump') else details.dict()
            try:
                es.index(index="entries", id=entry_id, body=doc)
                logger.info(f"Indexed/Updated entry {entry_id} in Elasticsearch")
                EVENTS_PROCESSED.inc()
            except Exception as e:
                logger.error(f"Failed to index entry {entry_id}: {e}")
                SYNC_ERRORS.inc()

async def wait_for_pg(dsn, retries=30, sleep=2):
    for i in range(retries):
        try:
            conn = await asyncpg.connect(dsn=dsn)

            logger.info(f"Postgres is up on {dsn}!")

            return conn
        except Exception as e:
            logger.error(f"Postgres not available yet: {e}")
            logger.warning(f"Waiting for postgres... ({i+1}/{retries})")

            await asyncio.sleep(sleep)

    raise RuntimeError("Postgres is not available")

async def main():
    conn = await wait_for_pg(PG_DSN)

    await conn.add_listener('entry_changed', handle_notify)

    logger.info("Listening for Postgres events on 'entry_changed' ...")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await conn.close()

asyncio.run(main()) 
