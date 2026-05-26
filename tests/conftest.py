"""Shared test fixtures for Stirlingpdf Agent."""

import pytest


@pytest.fixture
def mock_env(monkeypatch):
    """Set standard test environment variables."""
    monkeypatch.setenv("STIRLINGPDF_URL", "https://test.example.com")
    monkeypatch.setenv("STIRLINGPDF_TOKEN", "test-token-12345")
    monkeypatch.setenv("STIRLINGPDF_SSL_VERIFY", "False")
