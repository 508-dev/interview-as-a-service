"""Tests for interviewer ToS acceptance gating."""

import pytest
from django.urls import reverse

from interviewers.models import CURRENT_TOS_VERSION
from tests.factories import InterviewerFactory


@pytest.mark.django_db
class TestTosAcceptanceGate:
    def test_dashboard_redirects_when_tos_not_accepted(self, client):
        interviewer = InterviewerFactory(tos_accepted_version="")
        client.login(username=interviewer.user.username, password="testpass123")

        response = client.get(reverse("dashboard:home"))

        assert response.status_code == 302
        assert reverse("accounts:accept_tos") in response.url

    def test_dashboard_redirects_when_tos_version_stale(self, client):
        interviewer = InterviewerFactory(tos_accepted_version="0")
        client.login(username=interviewer.user.username, password="testpass123")

        response = client.get(reverse("dashboard:home"))

        assert response.status_code == 302
        assert reverse("accounts:accept_tos") in response.url

    def test_dashboard_loads_when_tos_accepted(self, client, client_with_interviewer):
        response = client_with_interviewer.get(reverse("dashboard:home"))
        assert response.status_code == 200

    def test_accept_tos_page_loads(self, client):
        interviewer = InterviewerFactory(tos_accepted_version="")
        client.login(username=interviewer.user.username, password="testpass123")

        response = client.get(reverse("accounts:accept_tos"))

        assert response.status_code == 200
        assert interviewer.user.get_full_name().encode() in response.content

    def test_accept_tos_with_correct_name_accepts_and_redirects(self, client):
        interviewer = InterviewerFactory(tos_accepted_version="")
        client.login(username=interviewer.user.username, password="testpass123")
        full_name = interviewer.user.get_full_name()

        response = client.post(
            reverse("accounts:accept_tos"),
            {"typed_name": full_name, "next": reverse("dashboard:home")},
        )

        assert response.status_code == 302
        assert response.url == reverse("dashboard:home")

        interviewer.refresh_from_db()
        assert interviewer.tos_accepted_version == CURRENT_TOS_VERSION
        assert interviewer.tos_accepted_at is not None

    def test_accept_tos_with_wrong_name_does_not_accept(self, client):
        interviewer = InterviewerFactory(tos_accepted_version="")
        client.login(username=interviewer.user.username, password="testpass123")

        response = client.post(
            reverse("accounts:accept_tos"),
            {"typed_name": "Someone Else", "next": reverse("dashboard:home")},
        )

        assert response.status_code == 200

        interviewer.refresh_from_db()
        assert interviewer.tos_accepted_version == ""
        assert interviewer.tos_accepted_at is None

    def test_accept_tos_name_match_is_case_insensitive(self, client):
        interviewer = InterviewerFactory(tos_accepted_version="")
        client.login(username=interviewer.user.username, password="testpass123")
        full_name = interviewer.user.get_full_name()

        response = client.post(
            reverse("accounts:accept_tos"),
            {"typed_name": full_name.upper(), "next": reverse("dashboard:home")},
        )

        assert response.status_code == 302
        interviewer.refresh_from_db()
        assert interviewer.tos_accepted_version == CURRENT_TOS_VERSION

    def test_already_accepted_interviewer_skips_accept_page(self, client, client_with_interviewer, interviewer):
        response = client_with_interviewer.get(reverse("accounts:accept_tos"))
        assert response.status_code == 302
        assert response.url == reverse("dashboard:home")
