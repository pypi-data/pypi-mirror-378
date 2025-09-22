"""
ProServe Framework Utility Functions
Helper functions and framework utilities
"""

from typing import List
from .service_models import Framework


def get_framework_by_name(name: str) -> Framework:
    """Get Framework enum by string name"""
    try:
        return Framework(name.lower())
    except ValueError:
        return Framework.UNKNOWN


def get_supported_frameworks() -> List[str]:
    """Get list of supported framework names"""
    return [f.value for f in Framework if f != Framework.UNKNOWN]


def is_web_framework(framework: Framework) -> bool:
    """Check if framework is a web framework"""
    web_frameworks = {
        Framework.FLASK, Framework.FASTAPI, Framework.DJANGO,
        Framework.STARLETTE, Framework.TORNADO, Framework.AIOHTTP,
        Framework.BOTTLE, Framework.CHERRYPY, Framework.PYRAMID,
        Framework.SANIC, Framework.QUART, Framework.EXPRESS
    }
    return framework in web_frameworks
