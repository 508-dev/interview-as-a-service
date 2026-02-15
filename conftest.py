"""pytest configuration and fixtures."""

import pytest
from django.contrib.auth.models import User

from tests.factories import BookingFactory, InterviewerFactory


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def interviewer(db, user):
    """Create a test interviewer."""
    return InterviewerFactory(user=user)


@pytest.fixture
def booking(db, interviewer):
    """Create a test booking."""
    return BookingFactory(interviewer=interviewer)


@pytest.fixture
def client_with_user(client, user):
    """Return a client logged in as the test user."""
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def client_with_interviewer(client, interviewer):
    """Return a client logged in as an interviewer."""
    client.login(username=interviewer.user.username, password="testpass123")
    return client
