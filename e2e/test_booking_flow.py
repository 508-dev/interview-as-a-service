"""E2E tests for the booking flow."""

from playwright.sync_api import Page, expect


def test_booking_start_page_loads(page: Page, base_url: str):
    """Test that the booking start page loads with cal.com embed."""
    # This assumes an interviewer with ID 1 exists
    page.goto(f"{base_url}/bookings/1/")
    expect(page.locator("#cal-embed")).to_be_visible()


def test_booking_form_requires_datetime(page: Page, base_url: str):
    """Test that booking form redirects without datetime."""
    page.goto(f"{base_url}/bookings/1/form/")
    # Should redirect back to start page
    expect(page).to_have_url(f"{base_url}/bookings/1/")


def test_booking_form_loads_with_datetime(page: Page, base_url: str):
    """Test that booking form loads with datetime parameter."""
    page.goto(f"{base_url}/bookings/1/form/?datetime=2025-06-01T10:00:00Z")

    # Form fields should be visible
    expect(page.locator("#customer_name")).to_be_visible()
    expect(page.locator("#customer_email")).to_be_visible()
    expect(page.locator("#customer_background")).to_be_visible()
    expect(page.locator("#interview_focus")).to_be_visible()


def test_booking_form_validation(page: Page, base_url: str):
    """Test that form validation works."""
    page.goto(f"{base_url}/bookings/1/form/?datetime=2025-06-01T10:00:00Z")

    # Try to submit without filling required fields
    submit = page.locator("button[type='submit']")
    submit.click()

    # HTML5 validation should prevent submission
    # The form should still be on the same page
    expect(page).to_have_url(f"{base_url}/bookings/1/form/?datetime=2025-06-01T10:00:00Z")


def test_booking_form_submission(page: Page, base_url: str):
    """Test filling out the booking form."""
    page.goto(f"{base_url}/bookings/1/form/?datetime=2025-06-01T10:00:00Z")

    # Fill out the form
    page.fill("#customer_name", "Test User")
    page.fill("#customer_email", "test@example.com")
    page.fill("#customer_background", "5 years of experience in backend development")
    page.fill("#interview_focus", "System design interviews")
    page.fill("#target_companies", "Google, Meta")
    page.fill("#additional_info", "I'm preparing for senior roles")

    # Note: Actual submission would redirect to Stripe
    # In E2E tests, you might mock Stripe or use test mode
    submit = page.locator("button[type='submit']")
    expect(submit).to_have_text("Continue to Payment")


def test_success_page_displays(page: Page, base_url: str):
    """Test that the success page displays correctly."""
    page.goto(f"{base_url}/bookings/success/")
    expect(page.locator("h1")).to_contain_text("Booking Confirmed")


def test_cancel_page_displays(page: Page, base_url: str):
    """Test that the cancel page displays correctly."""
    page.goto(f"{base_url}/bookings/cancel/")
    expect(page.locator("h1")).to_contain_text("Payment Cancelled")
