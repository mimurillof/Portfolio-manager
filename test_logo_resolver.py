"""Pruebas unitarias para ``logo_resolver``.

Estas pruebas son ligeras y no requieren acceso a internet; únicamente
validan la generación correcta de URLs.
"""
import unittest

from logo_resolver import CLEARBIT_BASE_URL, resolve_logo_url


class LogoResolverTests(unittest.TestCase):
    def test_symbol_override(self) -> None:
        logo_url = resolve_logo_url("AAPL")
        self.assertEqual(logo_url, CLEARBIT_BASE_URL.format(domain="apple.com"))

    def test_website_fallback(self) -> None:
        logo_url = resolve_logo_url("XYZ", website="https://example.org/about")
        self.assertEqual(logo_url, CLEARBIT_BASE_URL.format(domain="example.org"))

    def test_returns_none_when_unknown(self) -> None:
        self.assertIsNone(resolve_logo_url(""))
        self.assertIsNone(resolve_logo_url("UNLISTED"))


if __name__ == "__main__":
    unittest.main()
