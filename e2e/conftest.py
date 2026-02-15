"""Playwright E2E test fixtures."""

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the test server."""
    return "http://localhost:8000"


@pytest.fixture
def homepage(page: Page, base_url: str):
    """Navigate to homepage."""
    page.goto(base_url)
    return page


@pytest.fixture
def interviewers_page(page: Page, base_url: str):
    """Navigate to interviewers list page."""
    page.goto(f"{base_url}/interviewers/")
    return page


@pytest.fixture
def login_page(page: Page, base_url: str):
    """Navigate to login page."""
    page.goto(f"{base_url}/accounts/login/")
    return page
