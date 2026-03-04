from django.shortcuts import render

from interviewers.models import Interviewer


def home(request):
    """Homepage view."""
    featured_interviewers = Interviewer.objects.filter(is_active=True)[:6]
    return render(
        request,
        "pages/home.html",
        {"featured_interviewers": featured_interviewers},
    )


def about(request):
    """About 508.dev page."""
    return render(request, "pages/about.html")
