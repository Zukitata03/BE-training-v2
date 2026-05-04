import unittest
import uuid

import tests.env_defaults  # noqa: F401 — set env before app import
from main import app

from tests.http_support import auth_path, books_path, data_payload
from tests.integration_guard import skip_if_no_redis


class BooksTests(unittest.TestCase):
    """HTTP tests for books endpoints (integration-style via Sanic test client)."""

    def test_get_all_books(self):
        _, response = app.test_client.get(books_path())
        self.assertEqual(response.status, 200)
        data = data_payload(response)
        self.assertIsInstance(data, dict)
        self.assertGreaterEqual(data.get('n_books'), 0)
        self.assertIsInstance(data.get('books'), list)

    def test_get_book_by_id_not_found(self):
        fake_id = str(uuid.uuid4())
        _, response = app.test_client.get(books_path(fake_id))
        self.assertEqual(response.status, 404)

    def test_post_book_unauthorized(self):
        _, response = app.test_client.post(
            books_path(),
            json={
                'title': 'T',
                'authors': ['A'],
                'publisher': 'P',
            },
        )
        self.assertEqual(response.status, 401)

    def test_post_book_bad_json_missing_required(self):
        _, response = app.test_client.post(
            books_path(),
            json={'title': 'Only title'},
        )
        self.assertEqual(response.status, 400)

    def test_book_crud_with_auth(self):
        username = f'booktest_{uuid.uuid4().hex[:12]}'
        password = 'password123'

        _, reg = app.test_client.post(
            auth_path('/register'),
            json={'username': username, 'password': password},
        )
        self.assertEqual(reg.status, 201, reg.text)
        self.assertIn('message', data_payload(reg) or {})

        _, login = app.test_client.post(
            auth_path('/login'),
            json={'username': username, 'password': password},
        )
        self.assertEqual(login.status, 200, login.text)
        token = (data_payload(login) or {}).get('token')
        self.assertIsInstance(token, str)
        auth_header = {'Authorization': f'Bearer {token}'}

        payload = {
            'title': 'Test Book',
            'authors': ['Author One'],
            'publisher': 'Test Press',
            'description': 'Desc',
        }
        _, created = app.test_client.post(
            books_path(),
            json=payload,
            headers=auth_header,
        )
        self.assertEqual(created.status, 201, created.text)
        d = data_payload(created)
        self.assertEqual(d.get('message'), 'created')
        book = d.get('book')
        self.assertIsInstance(book, dict)
        self.assertEqual(book.get('owner'), username)
        book_id = book['_id']

        _, one = app.test_client.get(books_path(book_id))
        self.assertEqual(one.status, 200)
        self.assertEqual((data_payload(one) or {}).get('book', {}).get('_id'), book_id)

        new_payload = {
            'title': 'Test Book Updated',
            'authors': ['Author One', 'Author Two'],
            'publisher': 'Test Press',
        }
        _, updated = app.test_client.put(
            books_path(book_id),
            json=new_payload,
            headers=auth_header,
        )
        self.assertEqual(updated.status, 200, updated.text)
        du = data_payload(updated)
        self.assertEqual(du.get('message'), 'updated')
        self.assertEqual(du.get('book', {}).get('title'), 'Test Book Updated')

        _, deleted = app.test_client.delete(
            books_path(book_id),
            headers=auth_header,
        )
        self.assertEqual(deleted.status, 200, deleted.text)
        self.assertEqual((data_payload(deleted) or {}).get('message'), 'deleted')

        _, gone = app.test_client.get(books_path(book_id))
        self.assertEqual(gone.status, 404)


if __name__ == '__main__':
    unittest.main()
