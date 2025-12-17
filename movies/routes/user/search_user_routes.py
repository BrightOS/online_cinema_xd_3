
from fastapi import APIRouter
from elasticsearch import Elasticsearch

router = APIRouter(prefix="/search", tags=["User"])

es = Elasticsearch("http://localhost:9200")

@router.get("/")
async def search_entries(query: str, limit: int = 10, offset: int = 0):
    query_body = {
        "from": offset,
        "size": limit,
        "query": {
            "wildcard": {
                "status": {
                    "value": f"*{query.lower()}*",
                }
            }
        }
    }

    res = es.search(index="entries", body=query_body)

    return [hit["_source"] for hit in res["hits"]["hits"]]
