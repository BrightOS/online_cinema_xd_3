from .entry_admin_routes import router as entry_router
from .entry_locale_admin_routes import router as entry_locale_router
from .episode_admin_routes import router as episode_router
from .episode_locale_admin_routes import router as episode_locale_router
from .franchise_admin_routes import router as franchise_router
from .franchise_locale_admin_routes import router as franchise_locale_router
from .genre_admin_routes import router as genre_router
from .person_admin_routes import router as person_router
from .generate_test_data_admin_routes import router as generate_test_data_router

admin_routes = [
    entry_router,
    entry_locale_router,
    episode_router,
    episode_locale_router,
    franchise_router,
    franchise_locale_router,
    genre_router,
    person_router,
    generate_test_data_router,
]

__all__ = ["admin_routes"]
