from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bookings.models import Booking
from interviewers.models import InterviewSubject, Technology


@login_required
def dashboard_home(request):
    """Dashboard home with upcoming interviews."""
    # Check if user is an interviewer
    if not hasattr(request.user, "interviewer"):
        messages.error(request, "You don't have an interviewer profile.")
        return redirect("pages:home")

    interviewer = request.user.interviewer
    upcoming_bookings = Booking.objects.filter(
        interviewer=interviewer,
        scheduled_at__gte=timezone.now(),
        status__in=[Booking.Status.CONFIRMED, Booking.Status.PENDING],
    ).order_by("scheduled_at")[:10]

    past_bookings = Booking.objects.filter(
        interviewer=interviewer,
        scheduled_at__lt=timezone.now(),
    ).order_by("-scheduled_at")[:5]

    return render(
        request,
        "dashboard/home.html",
        {
            "upcoming_bookings": upcoming_bookings,
            "past_bookings": past_bookings,
            "interviewer": interviewer,
        },
    )


@login_required
def profile_edit(request):
    """Edit interviewer profile."""
    if not hasattr(request.user, "interviewer"):
        messages.error(request, "You don't have an interviewer profile.")
        return redirect("pages:home")

    interviewer = request.user.interviewer
    technologies = Technology.objects.all()
    subjects = InterviewSubject.objects.all()

    if request.method == "POST":
        # Update profile fields
        interviewer.bio = request.POST.get("bio", interviewer.bio)
        interviewer.companies = request.POST.get("companies", interviewer.companies)
        interviewer.hourly_rate = request.POST.get("hourly_rate", interviewer.hourly_rate)

        # Handle photo upload
        if "photo" in request.FILES:
            interviewer.photo = request.FILES["photo"]

        # Update technologies
        tech_ids = request.POST.getlist("technologies")
        interviewer.technologies.set(Technology.objects.filter(id__in=tech_ids))

        # Update subjects
        subject_ids = request.POST.getlist("subjects")
        interviewer.subjects.set(InterviewSubject.objects.filter(id__in=subject_ids))

        interviewer.save()
        messages.success(request, "Profile updated successfully!")

        # For HTMX requests, return the form partial
        if request.headers.get("HX-Request"):
            return render(
                request,
                "dashboard/partials/profile_form.html",
                {
                    "interviewer": interviewer,
                    "technologies": technologies,
                    "subjects": subjects,
                },
            )

        return redirect("dashboard:profile")

    return render(
        request,
        "dashboard/profile.html",
        {
            "interviewer": interviewer,
            "technologies": technologies,
            "subjects": subjects,
        },
    )


@login_required
def booking_detail(request, pk):
    """View booking details."""
    if not hasattr(request.user, "interviewer"):
        messages.error(request, "You don't have an interviewer profile.")
        return redirect("pages:home")

    booking = get_object_or_404(
        Booking,
        pk=pk,
        interviewer=request.user.interviewer,
    )

    return render(
        request,
        "dashboard/booking_detail.html",
        {"booking": booking},
    )


@login_required
def booking_complete(request, pk):
    """Mark a booking as completed."""
    if not hasattr(request.user, "interviewer"):
        return redirect("pages:home")

    booking = get_object_or_404(
        Booking,
        pk=pk,
        interviewer=request.user.interviewer,
    )

    if request.method == "POST":
        booking.status = Booking.Status.COMPLETED
        booking.save()
        messages.success(request, "Booking marked as completed.")

    return redirect("dashboard:booking_detail", pk=pk)
