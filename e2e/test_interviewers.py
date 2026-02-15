"""E2E tests for the interviewers pages."""

from playwright.sync_api import Page, expect


def test_interviewers_page_loads(interviewers_page: Page):
    """Test that the interviewers list page loads."""
    expect(interviewers_page).to_have_title("Find an Interviewer - 508.dev Interview Service")


def test_interviewers_has_filters(interviewers_page: Page):
    """Test that filter dropdowns are present."""
    tech_filter = interviewers_page.locator("#technology-filter")
    subject_filter = interviewers_page.locator("#subject-filter")

    expect(tech_filter).to_be_visible()
    expect(subject_filter).to_be_visible()


def test_interviewer_card_click_opens_modal(interviewers_page: Page):
    """Test that clicking an interviewer card opens a modal."""
    # This test assumes there's at least one interviewer in the database
    card = interviewers_page.locator(".interviewer-card").first
    card.click()

    # Wait for modal to appear
    modal = interviewers_page.locator(".modal-backdrop")
    expect(modal).to_be_visible()


def test_modal_has_book_now_button(interviewers_page: Page):
    """Test that the modal has a Book Now button."""
    card = interviewers_page.locator(".interviewer-card").first
    card.click()

    book_button = interviewers_page.locator(".modal .btn-primary")
    expect(book_button).to_have_text("Book Now")


def test_modal_close_button_works(interviewers_page: Page):
    """Test that the modal close button works."""
    card = interviewers_page.locator(".interviewer-card").first
    card.click()

    modal = interviewers_page.locator(".modal-backdrop")
    expect(modal).to_be_visible()

    close_button = interviewers_page.locator(".modal-close")
    close_button.click()

    expect(modal).not_to_be_visible()


def test_filter_updates_results(interviewers_page: Page):
    """Test that changing filters updates the results via HTMX."""
    tech_filter = interviewers_page.locator("#technology-filter")

    # Select a technology (assuming options exist)
    # This will trigger an HTMX request
    tech_filter.select_option(index=1)

    # Wait for HTMX to complete
    interviewers_page.wait_for_load_state("networkidle")

    # The grid should still be present
    grid = interviewers_page.locator("#interviewers-grid")
    expect(grid).to_be_visible()
