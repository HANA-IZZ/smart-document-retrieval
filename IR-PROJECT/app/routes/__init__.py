from .index_routes import register_index_routes
from .search_routes import register_search_routes
from .analytics_routes import register_analytics_routes
from .health_routes import register_health_routes

def register_all_routes(app):
    register_index_routes(app)
    register_search_routes(app)
    register_analytics_routes(app)
    register_health_routes(app)