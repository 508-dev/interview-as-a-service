"""Tests for Stripe webhook handling."""

import json
from unittest.mock import patch, MagicMock

import pytest
from django.urls import reverse

from bookings.models import Booking
from tests.factories import BookingFactory


@pytest.mark.django_db
class TestStripeWebhook:
    @patch("bookings.webhooks.stripe.Webhook.construct_event")
    @patch("bookings.webhooks.send_customer_confirmation")
    @patch("bookings.webhooks.send_interviewer_notification")
    def test_checkout_completed_updates_booking(
        self,
        mock_interviewer_email,
        mock_customer_email,
        mock_construct_event,
        client,
    ):
        # Create a pending booking
        booking = BookingFactory(status=Booking.Status.PENDING)

        # Mock the Stripe event
        mock_construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "payment_intent": "pi_test_123",
                    "metadata": {
                        "booking_id": str(booking.id),
                    },
                }
            },
        }

        response = client.post(
            reverse("bookings:stripe_webhook"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        assert response.status_code == 200

        # Verify booking was updated
        booking.refresh_from_db()
        assert booking.status == Booking.Status.CONFIRMED
        assert booking.stripe_payment_intent_id == "pi_test_123"

        # Verify emails were sent
        mock_customer_email.assert_called_once_with(booking)
        mock_interviewer_email.assert_called_once_with(booking)

    @patch("bookings.webhooks.stripe.Webhook.construct_event")
    def test_invalid_signature_returns_400(self, mock_construct_event, client):
        from stripe.error import SignatureVerificationError

        mock_construct_event.side_effect = SignatureVerificationError(
            "Invalid signature", "sig_header"
        )

        response = client.post(
            reverse("bookings:stripe_webhook"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid_signature",
        )

        assert response.status_code == 400

    @patch("bookings.webhooks.stripe.Webhook.construct_event")
    def test_unknown_event_type_returns_200(self, mock_construct_event, client):
        mock_construct_event.return_value = {
            "type": "some.other.event",
            "data": {"object": {}},
        }

        response = client.post(
            reverse("bookings:stripe_webhook"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        assert response.status_code == 200

    @patch("bookings.webhooks.stripe.Webhook.construct_event")
    def test_missing_booking_id_handled_gracefully(self, mock_construct_event, client):
        mock_construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "payment_intent": "pi_test_123",
                    "metadata": {},  # No booking_id
                }
            },
        }

        response = client.post(
            reverse("bookings:stripe_webhook"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        assert response.status_code == 200

    @patch("bookings.webhooks.stripe.Webhook.construct_event")
    def test_nonexistent_booking_handled_gracefully(
        self, mock_construct_event, client
    ):
        mock_construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "payment_intent": "pi_test_123",
                    "metadata": {
                        "booking_id": "99999",  # Doesn't exist
                    },
                }
            },
        }

        response = client.post(
            reverse("bookings:stripe_webhook"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        assert response.status_code == 200
