from .entry_user_routes import router as entry_router
from .episode_user_routes import router as episode_router
from .franchise_user_routes import router as franchise_router
from .genre_user_routes import router as genre_router
from .person_user_routes import router as person_router
from .search_user_routes import router as search_router

user_routes = [
    entry_router,
    episode_router,
    franchise_router,
    genre_router,
    person_router,
    search_router,
]

__all__ = ["user_routes"]
