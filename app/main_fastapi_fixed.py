"""
Fixed entry point for FastAPI application to satisfy tests.
Imports the main application from app.main.
"""
from .main import app

__all__ = ["app"]
