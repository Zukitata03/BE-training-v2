"""Skip integration HTTP tests when Redis (required for app startup) is not reachable."""
from __future__ import annotations

import os
import socket
import unittest


def _redis_tcp_open() -> bool:
    host = os.environ.get('REDIS_HOST', '127.0.0.1')
    port = int(os.environ.get('REDIS_PORT', '6379'))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.4)
    try:
        s.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


skip_if_no_redis = unittest.skipUnless(
    _redis_tcp_open(),
    'Redis not reachable at REDIS_HOST:REDIS_PORT (app before_server_start needs it). '
    'Start Redis or export REDIS_HOST for integration tests.',
)
