import os
from fastapi import APIRouter
from elasticsearch import Elasticsearch

from metrics import USER_SEARCH_TOTAL

router = APIRouter(prefix="/search", tags=["User"])

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = Elasticsearch(ELASTICSEARCH_URL)

@router.get("/")
async def search_entries(query: str, limit: int = 10, offset: int = 0):
    USER_SEARCH_TOTAL.labels(query_type="multi_match").inc()
    query_body = {
        "from": offset,
        "size": limit,
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "locales.title^3",
                    "locales.description^2",
                    "staff_names_search^1"
                ],
                "type": "bool_prefix"
            }
        }
    }
    res = es.search(index="entries", body=query_body)
    return [hit["_source"] for hit in res["hits"]["hits"]]
