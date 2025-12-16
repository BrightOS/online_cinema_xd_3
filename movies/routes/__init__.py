from .user import user_routes
from .admin import admin_routes

list_of_routes = [
    *user_routes,
    *admin_routes,
]

__all__ = ["list_of_routes"]
