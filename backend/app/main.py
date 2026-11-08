"""Run with: uvicorn app.main:app --reload --app-dir backend"""
from app.api.routes import app

__all__ = ["app"]
