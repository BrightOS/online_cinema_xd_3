import asyncio
from session import get_session
from routes.utils.entry import load_entry_details
from sqlalchemy import text
from elasticsearch import Elasticsearch
import os

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")

es = Elasticsearch(ELASTICSEARCH_URL)

async def get_person_by_id(db, person_id):
    result = await db.execute(
        text("SELECT id, name, en_name, birth_date FROM persons WHERE id = :id"),
        {"id": person_id}
    )
    row = result.fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "en_name": row[2],
        "birth_date": row[3]
    }

async def main():
    async for db in get_session():
        result = await db.execute(text("SELECT id FROM entries"))
        ids = [r[0] for r in result.fetchall()]

        for entry_id in ids:
            details = await load_entry_details(db, entry_id)
            if not details:
                continue

            enriched_staff = []
            staff_names_search = []

            for staff in details.staff:
                person = await get_person_by_id(db, staff.person_id)
                staff_dict = {
                    "role": staff.role,
                    "character_name": staff.character_name,
                    "entry_id": staff.entry_id,
                    "person_id": staff.person_id,
                    "person": person,
                }

                enriched_staff.append(staff_dict)

                if person:
                    if person.get("name"):
                        staff_names_search.append(person["name"])
                    if person.get("en_name"):
                        staff_names_search.append(person["en_name"])

            doc = details.model_dump() if hasattr(details, 'model_dump') else details.dict()
            doc["staff"] = enriched_staff
            doc["staff_names_search"] = " ".join(staff_names_search)

            es.index(index="entries", id=entry_id, body=doc)

            print(f"Indexed: id={details.id}, title={details.title}")

asyncio.run(main())
