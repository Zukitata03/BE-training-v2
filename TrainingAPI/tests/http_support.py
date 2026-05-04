"""Shared helpers for HTTP integration tests against ``main.app``."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any


def json_body(response) -> dict[str, Any]:
    return json.loads(response.text)


def data_payload(response) -> dict[str, Any] | list[Any] | None:
    """Top-level ``data`` from success responses."""
    return json_body(response).get('data')


@lru_cache(maxsize=1)
def _api_prefix_before_books() -> str:
    """Prefix before ``/books`` for list route (e.g. ``/v1`` or ````)."""
    from main import app

    for route in app.router.routes:
        methods = getattr(route, 'methods', None) or frozenset()
        if 'GET' not in methods:
            continue
        path = str(getattr(route, 'path', '') or '')
        if path.endswith('/books'):
            return path[: -len('/books')] or ''
    raise RuntimeError('No GET route ending with /books found; check Blueprint registration.')


def books_base() -> str:
    root = _api_prefix_before_books()
    return f'{root}/books' if root else '/books'


def books_path(*segments: str) -> str:
    """Collection URL or ``.../books/<segment>/...``."""
    base = books_base().rstrip('/')
    extra = [s.strip('/') for s in segments if s and s.strip('/')]
    if not extra:
        return base
    return '/'.join([base, *extra])


def auth_path(suffix: str) -> str:
    root = _api_prefix_before_books()
    base = f'{root}/auth' if root else '/auth'
    suf = suffix if suffix.startswith('/') else f'/{suffix}'
    return f'{base.rstrip("/")}{suf}'
