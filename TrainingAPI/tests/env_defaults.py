"""Apply defaults so the app can start during local ``unittest`` runs.

Import this module before ``from main import app`` in test modules.
Override any value with real environment variables when you run against Docker.
"""
from __future__ import annotations

import os

# RedisConfig defaults to host "redis" (compose service name); local tests need loopback.
os.environ.setdefault('REDIS_HOST', '127.0.0.1')
# Explicit Mongo URL helps CI / laptops without the same compose env block.
os.environ.setdefault('MONGO_CONNECTION_URL', 'mongodb://127.0.0.1:27017/')
os.environ.setdefault('MONGO_DATABASE', 'example_db')
