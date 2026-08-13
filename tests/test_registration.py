"""Tests for self-service interviewer registration and approval gating."""

import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse

from interviewers.models import Interviewer
from tests.factories import InterviewerFactory

VALID_REGISTRATION_DATA = {
    "username": "newapplicant",
    "email": "applicant@example.com",
    "first_name": "Ada",
    "last_name": "Lovelace",
    "password1": "a-very-uncommon-passphrase-42",
    "password2": "a-very-uncommon-passphrase-42",
}


@pytest.mark.django_db
class TestRegistration:
    def test_register_page_loads(self, client):
        response = client.get(reverse("accounts:register"))
        assert response.status_code == 200

    def test_valid_registration_creates_pending_interviewer_and_logs_in(self, client):
        response = client.post(reverse("accounts:register"), VALID_REGISTRATION_DATA)

        user = User.objects.get(username="newapplicant")
        interviewer = user.interviewer
        assert interviewer.approval_status == Interviewer.ApprovalStatus.PENDING
        assert user.check_password("a-very-uncommon-passphrase-42")

        # Logged in immediately, but bounced to the pending page rather than the dashboard.
        assert response.status_code == 302
        dashboard_response = client.get(reverse("dashboard:home"), follow=True)
        assert dashboard_response.redirect_chain[-1][0] == reverse("accounts:pending_approval")

    def test_registration_sends_admin_notification(self, client, settings):
        settings.ADMIN_NOTIFICATION_EMAIL = "admin@example.com"

        client.post(reverse("accounts:register"), VALID_REGISTRATION_DATA)

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["admin@example.com"]

    def test_registration_skips_notification_when_admin_email_unset(self, client, settings):
        settings.ADMIN_NOTIFICATION_EMAIL = ""

        client.post(reverse("accounts:register"), VALID_REGISTRATION_DATA)

        assert len(mail.outbox) == 0

    def test_weak_password_is_rejected(self, client):
        data = {**VALID_REGISTRATION_DATA, "password1": "password", "password2": "password"}
        response = client.post(reverse("accounts:register"), data)

        assert response.status_code == 200
        assert not User.objects.filter(username="newapplicant").exists()

    def test_mismatched_passwords_rejected(self, client):
        data = {**VALID_REGISTRATION_DATA, "password2": "something-else-entirely-99"}
        response = client.post(reverse("accounts:register"), data)

        assert response.status_code == 200
        assert not User.objects.filter(username="newapplicant").exists()

    def test_duplicate_username_rejected(self, client, user):
        data = {**VALID_REGISTRATION_DATA, "username": user.username}
        response = client.post(reverse("accounts:register"), data)

        assert response.status_code == 200
        assert User.objects.filter(username=user.username).count() == 1

    def test_duplicate_email_rejected(self, client, user):
        data = {**VALID_REGISTRATION_DATA, "email": user.email}
        response = client.post(reverse("accounts:register"), data)

        assert response.status_code == 200
        assert not User.objects.filter(username="newapplicant").exists()


@pytest.mark.django_db
class TestApprovalGate:
    def test_pending_interviewer_redirected_from_dashboard(self, client):
        interviewer = InterviewerFactory(approval_status=Interviewer.ApprovalStatus.PENDING)
        client.login(username=interviewer.user.username, password="testpass123")

        response = client.get(reverse("dashboard:home"))

        assert response.status_code == 302
        assert response.url == reverse("accounts:pending_approval")

    def test_pending_interviewer_redirected_from_profile_edit(self, client):
        interviewer = InterviewerFactory(approval_status=Interviewer.ApprovalStatus.PENDING)
        client.login(username=interviewer.user.username, password="testpass123")

        response = client.get(reverse("dashboard:profile"))

        assert response.status_code == 302
        assert response.url == reverse("accounts:pending_approval")

    def test_approved_interviewer_not_redirected(self, client_with_interviewer):
        response = client_with_interviewer.get(reverse("dashboard:home"))
        assert response.status_code == 200

    def test_pending_approval_page_loads_for_pending_interviewer(self, client):
        interviewer = InterviewerFactory(approval_status=Interviewer.ApprovalStatus.PENDING)
        client.login(username=interviewer.user.username, password="testpass123")

        response = client.get(reverse("accounts:pending_approval"))
        assert response.status_code == 200

    def test_pending_approval_page_redirects_once_approved(self, client_with_interviewer):
        response = client_with_interviewer.get(reverse("accounts:pending_approval"))
        assert response.status_code == 302
        assert response.url == reverse("dashboard:home")

    def test_pending_interviewer_excluded_from_public_list(self, client):
        pending = InterviewerFactory(approval_status=Interviewer.ApprovalStatus.PENDING)
        approved = InterviewerFactory(approval_status=Interviewer.ApprovalStatus.APPROVED)

        response = client.get(reverse("interviewers:list"))

        assert pending.display_name.encode() not in response.content
        assert approved.display_name.encode() in response.content

    def test_pending_interviewer_excluded_from_featured(self, client):
        pending = InterviewerFactory(approval_status=Interviewer.ApprovalStatus.PENDING)

        response = client.get(reverse("interviewers:featured"))

        assert pending.display_name.encode() not in response.content

    def test_pending_interviewer_detail_modal_404s(self, client):
        pending = InterviewerFactory(approval_status=Interviewer.ApprovalStatus.PENDING)

        response = client.get(reverse("interviewers:detail_modal", args=[pending.pk]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestAdminApprovalAction:
    def test_approve_action_flips_status_and_notifies(self, admin_client):
        interviewer = InterviewerFactory(approval_status=Interviewer.ApprovalStatus.PENDING)

        response = admin_client.post(
            reverse("admin:interviewers_interviewer_changelist"),
            {
                "action": "approve_interviewers",
                "_selected_action": [str(interviewer.pk)],
            },
            follow=True,
        )

        assert response.status_code == 200
        interviewer.refresh_from_db()
        assert interviewer.approval_status == Interviewer.ApprovalStatus.APPROVED
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [interviewer.user.email]
