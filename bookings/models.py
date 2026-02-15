from django.db import models

from interviewers.models import Interviewer


class Booking(models.Model):
    """A booking for an interview session."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Payment"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    interviewer = models.ForeignKey(
        Interviewer,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_background = models.TextField(
        help_text="Customer's background and experience level",
    )
    interview_focus = models.TextField(
        help_text="What the customer wants to be interviewed on",
    )
    target_companies = models.TextField(
        blank=True,
        help_text="Companies the customer is targeting (Google, startups, etc.)",
    )
    additional_info = models.TextField(
        blank=True,
        help_text="Any additional information from the customer",
    )
    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        help_text="Customer's resume (stored in MinIO)",
    )
    scheduled_at = models.DateTimeField(
        help_text="When the interview is scheduled",
    )
    duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Duration of the interview in minutes",
    )
    stripe_payment_intent_id = models.CharField(
        max_length=200,
        blank=True,
    )
    stripe_checkout_session_id = models.CharField(
        max_length=200,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    cal_booking_uid = models.CharField(
        max_length=200,
        blank=True,
        help_text="Cal.com booking UID",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"Booking with {self.interviewer} on {self.scheduled_at}"

    @property
    def amount_cents(self):
        """Calculate the amount in cents for Stripe."""
        hourly_rate = self.interviewer.hourly_rate
        hours = self.duration_minutes / 60
        return int(hourly_rate * hours * 100)
