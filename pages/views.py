from django.shortcuts import render

from interviewers.models import Interviewer


def home(request):
    """Homepage view."""
    featured_interviewers = Interviewer.objects.filter(is_active=True).exclude(cal_event_type_id="")[:6]
    return render(
        request,
        "pages/home.html",
        {"featured_interviewers": featured_interviewers},
    )
