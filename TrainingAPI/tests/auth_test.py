import unittest
import uuid

import tests.env_defaults  # noqa: F401 — set env before app import
from main import app

from tests.http_support import auth_path, data_payload
from tests.integration_guard import skip_if_no_redis



class AuthTests(unittest.TestCase):
    """HTTP tests for auth (register / login) endpoints."""

    def test_register_success(self):
        username = f'regtest_{uuid.uuid4().hex[:12]}'
        _, response = app.test_client.post(
            auth_path('/register'),
            json={'username': username, 'password': 'password123'},
        )
        self.assertEqual(response.status, 201, response.text)
        data = data_payload(response)
        self.assertIsInstance(data, dict)
        self.assertIn('message', data)

    def test_register_duplicate_username(self):
        username = f'dupuser_{uuid.uuid4().hex[:12]}'
        body = {'username': username, 'password': 'password123'}
        _, first = app.test_client.post(auth_path('/register'), json=body)
        self.assertEqual(first.status, 201, first.text)
        _, second = app.test_client.post(auth_path('/register'), json=body)
        self.assertEqual(second.status, 400, second.text)

    def test_register_password_too_short_schema(self):
        _, response = app.test_client.post(
            auth_path('/register'),
            json={'username': f'shortpw_{uuid.uuid4().hex[:8]}', 'password': 'short'},
        )
        self.assertEqual(response.status, 400, response.text)

    def test_login_success_returns_token(self):
        username = f'logintest_{uuid.uuid4().hex[:12]}'
        password = 'password123'
        _, reg = app.test_client.post(
            auth_path('/register'),
            json={'username': username, 'password': password},
        )
        self.assertEqual(reg.status, 201, reg.text)

        _, response = app.test_client.post(
            auth_path('/login'),
            json={'username': username, 'password': password},
        )
        self.assertEqual(response.status, 200, response.text)
        data = data_payload(response)
        self.assertIsInstance(data.get('token'), str)
        self.assertGreater(len(data['token']), 10)

    def test_login_unknown_user(self):
        _, response = app.test_client.post(
            auth_path('/login'),
            json={'username': 'nonexistent_user_xyz', 'password': 'password123'},
        )
        self.assertEqual(response.status, 401, response.text)

    def test_login_wrong_password(self):
        username = f'badlogin_{uuid.uuid4().hex[:12]}'
        _, reg = app.test_client.post(
            auth_path('/register'),
            json={'username': username, 'password': 'password123'},
        )
        self.assertEqual(reg.status, 201, reg.text)

        _, response = app.test_client.post(
            auth_path('/login'),
            json={'username': username, 'password': 'wrongpass1'},
        )
        self.assertEqual(response.status, 401, response.text)


if __name__ == '__main__':
    unittest.main()
