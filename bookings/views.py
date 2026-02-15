from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from interviewers.models import Interviewer

from .models import Booking
from .stripe import create_checkout_session, retrieve_checkout_session


def booking_start(request, interviewer_id):
    """Show cal.com embed for selecting a time slot."""
    interviewer = get_object_or_404(Interviewer, pk=interviewer_id, is_active=True)
    return render(
        request,
        "bookings/calendar.html",
        {"interviewer": interviewer},
    )


def booking_form(request, interviewer_id):
    """
    Show the booking form after selecting a time slot.
    Expects 'datetime' query parameter from cal.com callback.
    """
    interviewer = get_object_or_404(Interviewer, pk=interviewer_id, is_active=True)
    scheduled_at = request.GET.get("datetime")

    if not scheduled_at:
        messages.error(request, "Please select a time slot first.")
        return redirect("bookings:start", interviewer_id=interviewer_id)

    # Parse the datetime string from cal.com
    try:
        scheduled_datetime = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
    except ValueError:
        messages.error(request, "Invalid date/time format.")
        return redirect("bookings:start", interviewer_id=interviewer_id)

    return render(
        request,
        "bookings/form.html",
        {
            "interviewer": interviewer,
            "scheduled_at": scheduled_at,
            "scheduled_datetime": scheduled_datetime,
        },
    )


@require_POST
def create_booking(request, interviewer_id):
    """Create a booking and redirect to Stripe checkout."""
    interviewer = get_object_or_404(Interviewer, pk=interviewer_id, is_active=True)

    # Parse scheduled datetime
    scheduled_at = request.POST.get("scheduled_at")
    try:
        scheduled_datetime = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        messages.error(request, "Invalid date/time.")
        return redirect("bookings:start", interviewer_id=interviewer_id)

    # Create booking with pending status
    booking = Booking.objects.create(
        interviewer=interviewer,
        customer_name=request.POST.get("customer_name", ""),
        customer_email=request.POST.get("customer_email", ""),
        customer_background=request.POST.get("customer_background", ""),
        interview_focus=request.POST.get("interview_focus", ""),
        target_companies=request.POST.get("target_companies", ""),
        additional_info=request.POST.get("additional_info", ""),
        scheduled_at=scheduled_datetime,
        duration_minutes=int(request.POST.get("duration_minutes", 60)),
        status=Booking.Status.PENDING,
    )

    # Handle resume upload
    if "resume" in request.FILES:
        booking.resume = request.FILES["resume"]
        booking.save()

    # Create Stripe checkout session
    try:
        session = create_checkout_session(booking, request)
        booking.stripe_checkout_session_id = session.id
        booking.save()
        return redirect(session.url)
    except Exception as e:
        booking.delete()
        messages.error(request, f"Payment setup failed: {str(e)}")
        return redirect("bookings:start", interviewer_id=interviewer_id)


def checkout_success(request):
    """Handle successful Stripe checkout."""
    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(request, "Invalid checkout session.")
        return redirect("pages:home")

    try:
        session = retrieve_checkout_session(session_id)
        booking_id = session.metadata.get("booking_id")

        if booking_id:
            booking = Booking.objects.get(id=booking_id)
            # The webhook will handle status update, but we can show the booking info
            return render(
                request,
                "bookings/success.html",
                {"booking": booking},
            )
    except Exception:
        pass

    return render(request, "bookings/success.html", {"booking": None})


def checkout_cancel(request):
    """Handle cancelled Stripe checkout."""
    booking_id = request.GET.get("booking_id")

    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id, status=Booking.Status.PENDING)
            booking.status = Booking.Status.CANCELLED
            booking.save()
        except Booking.DoesNotExist:
            pass

    return render(request, "bookings/cancel.html")
