"""Email notification functions for bookings."""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_customer_confirmation(booking):
    """Send booking confirmation email to customer."""
    subject = f"Interview Booking Confirmed - {booking.scheduled_at.strftime('%B %d, %Y')}"

    html_message = render_to_string(
        "emails/customer_confirmation.html",
        {"booking": booking},
    )

    text_message = f"""
Your interview session has been confirmed!

Interviewer: {booking.interviewer.display_name}
Date: {booking.scheduled_at.strftime('%B %d, %Y at %I:%M %p %Z')}
Duration: {booking.duration_minutes} minutes

What you'll be focusing on:
{booking.interview_focus}

We'll send you a calendar invite with the meeting link.

Thank you for booking with 508.dev Interview Service!
    """

    send_mail(
        subject=subject,
        message=text_message.strip(),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.customer_email],
        html_message=html_message,
        fail_silently=True,
    )


def send_interviewer_notification(booking):
    """Send new booking notification to interviewer."""
    subject = f"New Interview Booking - {booking.customer_name}"

    html_message = render_to_string(
        "emails/interviewer_notification.html",
        {"booking": booking},
    )

    text_message = f"""
You have a new interview booking!

Customer: {booking.customer_name}
Email: {booking.customer_email}
Date: {booking.scheduled_at.strftime('%B %d, %Y at %I:%M %p %Z')}
Duration: {booking.duration_minutes} minutes

Background:
{booking.customer_background}

Interview Focus:
{booking.interview_focus}

Target Companies:
{booking.target_companies or 'Not specified'}

Additional Info:
{booking.additional_info or 'None'}

Log in to your dashboard to view more details and download their resume (if provided).
    """

    send_mail(
        subject=subject,
        message=text_message.strip(),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.interviewer.user.email],
        html_message=html_message,
        fail_silently=True,
    )
