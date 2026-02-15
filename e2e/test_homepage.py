"""E2E tests for the homepage."""

from playwright.sync_api import Page, expect


def test_homepage_loads(homepage: Page):
    """Test that the homepage loads correctly."""
    expect(homepage).to_have_title("508.dev Interview Service - Practice with Top Engineers")


def test_homepage_has_hero_section(homepage: Page):
    """Test that the hero section is present."""
    hero = homepage.locator(".hero")
    expect(hero).to_be_visible()
    expect(hero.locator("h1")).to_contain_text("Ace Your Technical Interview")


def test_homepage_has_cta_button(homepage: Page):
    """Test that the call-to-action button is present."""
    cta = homepage.locator(".hero .btn-primary")
    expect(cta).to_be_visible()
    expect(cta).to_have_text("Find an Interviewer")


def test_homepage_has_how_it_works(homepage: Page):
    """Test that the How It Works section is present."""
    section = homepage.locator("text=How It Works")
    expect(section).to_be_visible()

    steps = homepage.locator(".step")
    expect(steps).to_have_count(3)


def test_homepage_has_testimonials(homepage: Page):
    """Test that testimonials are present."""
    testimonials = homepage.locator(".testimonial")
    expect(testimonials).to_have_count(3)


def test_navigation_to_interviewers(homepage: Page):
    """Test navigation to interviewers page."""
    homepage.click("text=Find an Interviewer")
    expect(homepage).to_have_url("/interviewers/")


def test_navigation_to_login(homepage: Page):
    """Test navigation to login page."""
    homepage.click("text=Interviewer Login")
    expect(homepage).to_have_url("/accounts/login/")
