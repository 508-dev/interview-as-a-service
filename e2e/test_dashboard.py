"""E2E tests for the interviewer dashboard."""

from playwright.sync_api import Page, expect


def test_dashboard_requires_login(page: Page, base_url: str):
    """Test that dashboard redirects to login when not authenticated."""
    page.goto(f"{base_url}/dashboard/")
    expect(page).to_have_url(f"{base_url}/accounts/login/?next=/dashboard/")


def test_login_page_loads(login_page: Page):
    """Test that the login page loads correctly."""
    expect(login_page).to_have_title("Interviewer Login - 508.dev Interview Service")
    expect(login_page.locator("h1")).to_have_text("Interviewer Login")


def test_login_form_has_required_fields(login_page: Page):
    """Test that login form has username and password fields."""
    expect(login_page.locator("#id_username")).to_be_visible()
    expect(login_page.locator("#id_password")).to_be_visible()


def test_login_with_invalid_credentials(login_page: Page):
    """Test login with invalid credentials shows error."""
    login_page.fill("#id_username", "wronguser")
    login_page.fill("#id_password", "wrongpass")
    login_page.click("button[type='submit']")

    # Should show error message
    error = login_page.locator(".message-error")
    expect(error).to_be_visible()


def test_successful_login_redirects_to_dashboard(login_page: Page, base_url: str):
    """Test that successful login redirects to dashboard."""
    # This assumes a test user exists with these credentials
    login_page.fill("#id_username", "testinterviewer")
    login_page.fill("#id_password", "testpass123")
    login_page.click("button[type='submit']")

    # Should redirect to dashboard
    expect(login_page).to_have_url(f"{base_url}/dashboard/")


def test_dashboard_shows_welcome_message(page: Page, base_url: str):
    """Test that dashboard shows welcome message after login."""
    # Login first
    page.goto(f"{base_url}/accounts/login/")
    page.fill("#id_username", "testinterviewer")
    page.fill("#id_password", "testpass123")
    page.click("button[type='submit']")

    expect(page.locator("h1")).to_contain_text("Welcome")


def test_dashboard_sidebar_navigation(page: Page, base_url: str):
    """Test dashboard sidebar navigation."""
    # Login first
    page.goto(f"{base_url}/accounts/login/")
    page.fill("#id_username", "testinterviewer")
    page.fill("#id_password", "testpass123")
    page.click("button[type='submit']")

    # Click on Edit Profile in sidebar
    page.click("text=Edit Profile")
    expect(page).to_have_url(f"{base_url}/dashboard/profile/")


def test_profile_edit_form(page: Page, base_url: str):
    """Test profile edit form loads with current data."""
    # Login first
    page.goto(f"{base_url}/accounts/login/")
    page.fill("#id_username", "testinterviewer")
    page.fill("#id_password", "testpass123")
    page.click("button[type='submit']")

    # Navigate to profile
    page.goto(f"{base_url}/dashboard/profile/")

    # Form fields should be visible
    expect(page.locator("#bio")).to_be_visible()
    expect(page.locator("#hourly_rate")).to_be_visible()
    expect(page.locator("#companies")).to_be_visible()


def test_logout(page: Page, base_url: str):
    """Test logout functionality."""
    # Login first
    page.goto(f"{base_url}/accounts/login/")
    page.fill("#id_username", "testinterviewer")
    page.fill("#id_password", "testpass123")
    page.click("button[type='submit']")

    # Click logout
    page.click("text=Logout")

    # Should be redirected to homepage
    expect(page).to_have_url(f"{base_url}/")
