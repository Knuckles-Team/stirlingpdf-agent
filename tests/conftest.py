"""Shared test fixtures for Stirlingpdf Agent."""

import pytest


@pytest.fixture
def mock_env(monkeypatch):
    """Set standard test environment variables."""
    monkeypatch.setenv("STIRLINGPDF_URL", "https://test.example.com")
    monkeypatch.setenv("STIRLINGPDF_API_KEY", "test-token-12345")
