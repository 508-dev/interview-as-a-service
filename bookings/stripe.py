"""Stripe checkout session management."""

import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(booking, request):
    """
    Create a Stripe checkout session for a booking.

    Returns the checkout session object.
    """
    success_url = request.build_absolute_uri(
        reverse("bookings:success") + f"?session_id={{CHECKOUT_SESSION_ID}}"
    )
    cancel_url = request.build_absolute_uri(
        reverse("bookings:cancel") + f"?booking_id={booking.id}"
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": booking.amount_cents,
                    "product_data": {
                        "name": f"Interview Session with {booking.interviewer.display_name}",
                        "description": f"{booking.duration_minutes} minute interview session",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=booking.customer_email,
        metadata={
            "booking_id": str(booking.id),
            "interviewer_id": str(booking.interviewer.id),
        },
    )

    return session


def retrieve_checkout_session(session_id):
    """Retrieve a Stripe checkout session by ID."""
    return stripe.checkout.Session.retrieve(session_id)
