"""Tests for Django models."""

import pytest
from decimal import Decimal

from interviewers.models import Interviewer, Technology, InterviewSubject
from bookings.models import Booking
from tests.factories import (
    BookingFactory,
    InterviewerFactory,
    TechnologyFactory,
    InterviewSubjectFactory,
)


@pytest.mark.django_db
class TestTechnology:
    def test_str_representation(self):
        tech = TechnologyFactory(name="Python")
        assert str(tech) == "Python"

    def test_slug_is_unique(self):
        tech1 = TechnologyFactory(name="React", slug="react")
        with pytest.raises(Exception):
            TechnologyFactory(name="React 2", slug="react")


@pytest.mark.django_db
class TestInterviewSubject:
    def test_str_representation(self):
        subject = InterviewSubjectFactory(name="System Design")
        assert str(subject) == "System Design"


@pytest.mark.django_db
class TestInterviewer:
    def test_str_representation(self):
        interviewer = InterviewerFactory()
        expected = interviewer.user.get_full_name() or interviewer.user.username
        assert str(interviewer) == expected

    def test_display_name_uses_full_name(self):
        interviewer = InterviewerFactory()
        interviewer.user.first_name = "John"
        interviewer.user.last_name = "Doe"
        interviewer.user.save()
        assert interviewer.display_name == "John Doe"

    def test_display_name_falls_back_to_username(self):
        interviewer = InterviewerFactory()
        interviewer.user.first_name = ""
        interviewer.user.last_name = ""
        interviewer.user.save()
        assert interviewer.display_name == interviewer.user.username

    def test_company_list_parses_comma_separated(self):
        interviewer = InterviewerFactory(companies="Google, Meta, Amazon")
        assert interviewer.company_list == ["Google", "Meta", "Amazon"]

    def test_company_list_empty_string(self):
        interviewer = InterviewerFactory(companies="")
        assert interviewer.company_list == []

    def test_many_to_many_technologies(self):
        tech1 = TechnologyFactory(name="Python")
        tech2 = TechnologyFactory(name="JavaScript")
        interviewer = InterviewerFactory(technologies=[tech1, tech2])
        assert tech1 in interviewer.technologies.all()
        assert tech2 in interviewer.technologies.all()


@pytest.mark.django_db
class TestBooking:
    def test_str_representation(self):
        booking = BookingFactory()
        assert str(booking).startswith("Booking with")

    def test_amount_cents_calculation(self):
        interviewer = InterviewerFactory(hourly_rate=Decimal("150.00"))
        booking = BookingFactory(interviewer=interviewer, duration_minutes=60)
        assert booking.amount_cents == 15000  # $150.00 in cents

    def test_amount_cents_half_hour(self):
        interviewer = InterviewerFactory(hourly_rate=Decimal("100.00"))
        booking = BookingFactory(interviewer=interviewer, duration_minutes=30)
        assert booking.amount_cents == 5000  # $50.00 in cents

    def test_status_choices(self):
        booking = BookingFactory(status=Booking.Status.PENDING)
        assert booking.status == "pending"

        booking.status = Booking.Status.CONFIRMED
        booking.save()
        assert booking.status == "confirmed"

    def test_default_status_is_pending(self):
        interviewer = InterviewerFactory()
        booking = Booking.objects.create(
            interviewer=interviewer,
            customer_name="Test",
            customer_email="test@example.com",
            customer_background="Background",
            interview_focus="Focus",
            scheduled_at="2025-01-01T10:00:00Z",
        )
        assert booking.status == Booking.Status.PENDING
