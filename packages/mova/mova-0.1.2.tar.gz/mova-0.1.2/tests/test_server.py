#!/usr/bin/env python3

"""Testy jednostkowe dla serwera Mova."""

import unittest
import os
import sys

# Dodaj ścieżkę do serwera, aby można było zaimportować moduł
sys.path.append(os.path.join(os.path.dirname(__file__), '../server'))
from app import app
from fastapi.testclient import TestClient

class TestMovaServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mova Server', response.content)

    def test_websocket_endpoint(self):
        # Testowanie WebSocket wymaga specjalnego podejścia, na razie pomijamy
        pass

if __name__ == '__main__':
    unittest.main()
