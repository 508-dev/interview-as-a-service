from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from interviewers.emails import send_registration_notification
from interviewers.models import CURRENT_TOS_VERSION, Interviewer

from .forms import RegistrationForm


def login_view(request):
    """Login view for interviewers."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", "dashboard:home")
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """Logout view."""
    logout(request)
    return redirect("pages:home")


def register_view(request):
    """Let a prospective interviewer request an account.

    Creates the User and a pending Interviewer profile, then logs them in --
    dashboard access itself stays blocked (see
    interviewers.middleware.ApprovalRequiredMiddleware) until an admin
    approves the account from Django admin.
    """
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            interviewer = Interviewer.objects.create(
                user=user,
                bio="",
                hourly_rate=0,
                approval_status=Interviewer.ApprovalStatus.PENDING,
            )
            login(request, user)
            send_registration_notification(interviewer, request)
            messages.success(request, "Thanks for applying! We'll review your request shortly.")
            return redirect("dashboard:home")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def pending_approval_view(request):
    """Shown to a logged-in interviewer whose account isn't approved yet."""
    interviewer = getattr(request.user, "interviewer", None)
    if interviewer is None:
        messages.error(request, "You don't have an interviewer profile.")
        return redirect("pages:home")

    if interviewer.is_approved:
        return redirect("dashboard:home")

    return render(request, "accounts/pending_approval.html")


def _safe_next_url(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_url
    return "dashboard:home"


@login_required
def accept_tos_view(request):
    """Require interviewers to type their name to accept the current ToS."""
    if not hasattr(request.user, "interviewer"):
        messages.error(request, "You don't have an interviewer profile.")
        return redirect("pages:home")

    interviewer = request.user.interviewer
    next_url = _safe_next_url(request)

    if interviewer.has_accepted_current_tos:
        return redirect(next_url)

    expected_name = request.user.get_full_name() or request.user.username

    if request.method == "POST":
        typed_name = request.POST.get("typed_name", "").strip()
        if typed_name.casefold() == expected_name.casefold():
            interviewer.tos_accepted_version = CURRENT_TOS_VERSION
            interviewer.tos_accepted_at = timezone.now()
            interviewer.save(update_fields=["tos_accepted_version", "tos_accepted_at"])
            return redirect(next_url)
        messages.error(request, f'Please type your name exactly as "{expected_name}" to accept.')

    return render(
        request,
        "accounts/accept_tos.html",
        {
            "expected_name": expected_name,
            "next": next_url,
            "tos_version": CURRENT_TOS_VERSION,
        },
    )
