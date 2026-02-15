"""Tests for Django views."""

import pytest
from django.urls import reverse

from tests.factories import InterviewerFactory, BookingFactory, TechnologyFactory


@pytest.mark.django_db
class TestHomepage:
    def test_homepage_loads(self, client):
        response = client.get(reverse("pages:home"))
        assert response.status_code == 200
        assert b"508.dev" in response.content

    def test_homepage_shows_featured_interviewers_section(self, client):
        InterviewerFactory()
        response = client.get(reverse("pages:home"))
        assert b"Featured Interviewers" in response.content


@pytest.mark.django_db
class TestInterviewersList:
    def test_list_loads(self, client):
        response = client.get(reverse("interviewers:list"))
        assert response.status_code == 200

    def test_list_shows_active_interviewers(self, client):
        active = InterviewerFactory(is_active=True)
        inactive = InterviewerFactory(is_active=False)
        response = client.get(reverse("interviewers:list"))
        assert active.display_name.encode() in response.content
        assert inactive.display_name.encode() not in response.content

    def test_filter_by_technology(self, client):
        tech = TechnologyFactory(name="Python", slug="python")
        with_tech = InterviewerFactory(technologies=[tech])
        without_tech = InterviewerFactory()

        response = client.get(reverse("interviewers:list") + "?technology=python")
        assert response.status_code == 200

    def test_featured_interviewers_htmx(self, client):
        InterviewerFactory()
        response = client.get(
            reverse("interviewers:featured"),
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestInterviewerDetailModal:
    def test_modal_loads(self, client):
        interviewer = InterviewerFactory()
        response = client.get(
            reverse("interviewers:detail_modal", kwargs={"pk": interviewer.pk})
        )
        assert response.status_code == 200
        assert interviewer.display_name.encode() in response.content

    def test_modal_404_for_inactive(self, client):
        interviewer = InterviewerFactory(is_active=False)
        response = client.get(
            reverse("interviewers:detail_modal", kwargs={"pk": interviewer.pk})
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestBookingViews:
    def test_booking_start_loads(self, client):
        interviewer = InterviewerFactory()
        response = client.get(
            reverse("bookings:start", kwargs={"interviewer_id": interviewer.pk})
        )
        assert response.status_code == 200

    def test_booking_form_requires_datetime(self, client):
        interviewer = InterviewerFactory()
        response = client.get(
            reverse("bookings:form", kwargs={"interviewer_id": interviewer.pk})
        )
        # Should redirect back to start if no datetime
        assert response.status_code == 302

    def test_booking_form_loads_with_datetime(self, client):
        interviewer = InterviewerFactory()
        response = client.get(
            reverse("bookings:form", kwargs={"interviewer_id": interviewer.pk})
            + "?datetime=2025-06-01T10:00:00Z"
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestDashboardViews:
    def test_dashboard_requires_login(self, client):
        response = client.get(reverse("dashboard:home"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_dashboard_requires_interviewer_profile(self, client, user):
        client.force_login(user)
        response = client.get(reverse("dashboard:home"))
        # Should redirect with error message
        assert response.status_code == 302

    def test_dashboard_loads_for_interviewer(self, client, interviewer):
        client.force_login(interviewer.user)
        response = client.get(reverse("dashboard:home"))
        assert response.status_code == 200
        assert b"Welcome" in response.content

    def test_profile_edit_loads(self, client, interviewer):
        client.force_login(interviewer.user)
        response = client.get(reverse("dashboard:profile"))
        assert response.status_code == 200

    def test_booking_detail_loads(self, client, interviewer):
        booking = BookingFactory(interviewer=interviewer)
        client.force_login(interviewer.user)
        response = client.get(
            reverse("dashboard:booking_detail", kwargs={"pk": booking.pk})
        )
        assert response.status_code == 200

    def test_booking_detail_requires_ownership(self, client, interviewer):
        # Create booking for different interviewer
        other_booking = BookingFactory()
        client.force_login(interviewer.user)
        response = client.get(
            reverse("dashboard:booking_detail", kwargs={"pk": other_booking.pk})
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestAuthViews:
    def test_login_page_loads(self, client):
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 200

    def test_login_redirects_authenticated_user(self, client, user):
        client.force_login(user)
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 302

    def test_logout_works(self, client, user):
        client.force_login(user)
        response = client.get(reverse("accounts:logout"))
        assert response.status_code == 302
