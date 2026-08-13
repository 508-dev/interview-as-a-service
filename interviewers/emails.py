"""Email notification functions for interviewer registration/approval."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def send_registration_notification(interviewer, request):
    """Notify an admin that a new interviewer has requested to register."""
    if not settings.ADMIN_NOTIFICATION_EMAIL:
        logger.warning(
            "ADMIN_NOTIFICATION_EMAIL is not set; skipping registration notification for %s",
            interviewer.user.username,
        )
        return

    admin_url = request.build_absolute_uri(
        reverse("admin:interviewers_interviewer_change", args=[interviewer.pk])
    )
    subject = f"New interviewer registration - {interviewer.display_name}"
    message = f"""
{interviewer.display_name} ({interviewer.user.email}) just requested an interviewer account.

Review and approve them from Django admin:
{admin_url}
    """

    send_mail(
        subject=subject,
        message=message.strip(),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
    )


def send_approval_notification(interviewer):
    """Let a newly-approved interviewer know they can start using their account."""
    subject = "Your interviewer account has been approved"
    message = f"""
Hi {interviewer.display_name},

Your interviewer account has been approved! You can now log in and set up your profile.

Thanks for joining 508.dev Interview Service!
    """

    send_mail(
        subject=subject,
        message=message.strip(),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[interviewer.user.email],
    )
