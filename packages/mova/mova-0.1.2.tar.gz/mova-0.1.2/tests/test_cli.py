#!/usr/bin/env python3

"""Testy jednostkowe dla CLI Mova."""

import unittest
import sys
import os

# Dodaj ścieżkę do CLI, aby można było zaimportować moduł
sys.path.append(os.path.join(os.path.dirname(__file__), '../cli'))
from mova import main

class TestMovaCLI(unittest.TestCase):
    def setUp(self):
        self.original_argv = sys.argv

    def tearDown(self):
        sys.argv = self.original_argv

    def test_shell_command(self):
        sys.argv = ['mova.py', 'shell', 'ls -la']
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)

    def test_http_command(self):
        sys.argv = ['mova.py', 'http', '--port', '8094', 'localhost', 'console.log("Test")']
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)

    def test_info_command(self):
        sys.argv = ['mova.py', 'info', 'Testowy log informacyjny']
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)

    def test_no_command(self):
        sys.argv = ['mova.py']
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
