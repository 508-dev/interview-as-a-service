from django.contrib.auth.models import User
from django.db import models

# Bump this whenever the Interviewer ToS text changes to re-prompt everyone.
CURRENT_TOS_VERSION = "1"


class Technology(models.Model):
    """Technologies that interviewers are proficient in (React, Python, etc.)"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "technologies"
        ordering = ["name"]

    def __str__(self):
        return self.name


class InterviewSubject(models.Model):
    """Interview subjects (Frontend, System Design, etc.)"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class HumanLanguage(models.Model):
    """Human languages an interviewer can conduct interviews in."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Interviewer(models.Model):
    """Interviewer profile linked to Django auth user."""

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="interviewer")
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        help_text="Whether this interviewer has been approved to use the platform.",
    )
    bio = models.TextField(help_text="Brief biography and experience")
    photo = models.ImageField(upload_to="interviewers/", blank=True)
    cal_link = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Cal.com link for booking, e.g. 'username/event-slug'. Profile is hidden from the public site until this is set.",
    )
    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Hourly rate in USD",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the interviewer is available for bookings",
    )
    technologies = models.ManyToManyField(
        Technology,
        related_name="interviewers",
        blank=True,
    )
    subjects = models.ManyToManyField(
        InterviewSubject,
        related_name="interviewers",
        blank=True,
    )
    languages = models.ManyToManyField(
        HumanLanguage,
        related_name="interviewers",
        blank=True,
    )
    companies = models.TextField(
        blank=True,
        help_text="Comma-separated list of companies worked at",
    )
    tos_accepted_version = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Version of the Interviewer ToS this interviewer has accepted",
    )
    tos_accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the interviewer accepted the current ToS version",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def has_accepted_current_tos(self):
        return self.tos_accepted_version == CURRENT_TOS_VERSION

    @property
    def is_approved(self):
        return self.approval_status == self.ApprovalStatus.APPROVED

    @property
    def is_bookable(self):
        return self.is_active and bool(self.cal_link)

    @property
    def company_list(self):
        if not self.companies:
            return []
        return [c.strip() for c in self.companies.split(",") if c.strip()]
