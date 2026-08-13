"""Factory classes for test data generation."""

from datetime import timedelta
from decimal import Decimal

import factory
from django.contrib.auth.models import User
from django.utils import timezone

from bookings.models import Booking
from interviewers.models import CURRENT_TOS_VERSION, HumanLanguage, Interviewer, InterviewSubject, Technology


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class TechnologyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Technology

    name = factory.Sequence(lambda n: f"Technology {n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class InterviewSubjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InterviewSubject

    name = factory.Sequence(lambda n: f"Subject {n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class HumanLanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HumanLanguage

    name = factory.Sequence(lambda n: f"Language {n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class InterviewerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Interviewer

    user = factory.SubFactory(UserFactory)
    bio = factory.Faker("paragraph")
    cal_link = factory.Sequence(lambda n: f"interviewer-{n}/mock-interview")
    hourly_rate = Decimal("150.00")
    is_active = True
    approval_status = Interviewer.ApprovalStatus.APPROVED
    companies = "Google, Meta, Amazon"
    tos_accepted_version = CURRENT_TOS_VERSION
    tos_accepted_at = factory.LazyAttribute(lambda obj: timezone.now() if obj.tos_accepted_version else None)

    @factory.post_generation
    def technologies(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tech in extracted:
                self.technologies.add(tech)

    @factory.post_generation
    def subjects(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for subject in extracted:
                self.subjects.add(subject)

    @factory.post_generation
    def languages(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for language in extracted:
                self.languages.add(language)


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    interviewer = factory.SubFactory(InterviewerFactory)
    customer_name = factory.Faker("name")
    customer_email = factory.Faker("email")
    customer_background = factory.Faker("paragraph")
    interview_focus = factory.Faker("sentence")
    target_companies = "Google, startups"
    scheduled_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    duration_minutes = 60
    status = Booking.Status.CONFIRMED
