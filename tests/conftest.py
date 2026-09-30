"""Shared test setup.

Your app reads the database URL and the Gemini key when modules are imported.
On GitHub there is no .env file, so we provide harmless dummy values.

load_dotenv() does NOT overwrite values that already exist, so on your own
computer the real values from .env are used (integration tests need them).
"""
import os

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("GEMINI_API_KEY", "dummy-key")
