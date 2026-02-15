"""Stripe webhook handlers."""

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .emails import send_customer_confirmation, send_interviewer_notification
from .models import Booking


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse("Invalid signature", status=400)

    # Handle checkout.session.completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_checkout_completed(session)

    return HttpResponse(status=200)


def handle_checkout_completed(session):
    """Handle successful checkout completion."""
    booking_id = session.get("metadata", {}).get("booking_id")

    if not booking_id:
        return

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return

    # Update booking status
    booking.status = Booking.Status.CONFIRMED
    booking.stripe_payment_intent_id = session.get("payment_intent", "")
    booking.save()

    # Send confirmation emails
    send_customer_confirmation(booking)
    send_interviewer_notification(booking)
