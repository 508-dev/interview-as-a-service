from django.contrib.auth.models import User
from django.db import models


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


class Interviewer(models.Model):
    """Interviewer profile linked to Django auth user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="interviewer")
    bio = models.TextField(help_text="Brief biography and experience")
    photo = models.ImageField(upload_to="interviewers/", blank=True)
    cal_event_type_id = models.CharField(
        max_length=100,
        help_text="Cal.com Event Type ID for booking",
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
    companies = models.TextField(
        blank=True,
        help_text="Comma-separated list of companies worked at",
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
    def company_list(self):
        if not self.companies:
            return []
        return [c.strip() for c in self.companies.split(",") if c.strip()]
