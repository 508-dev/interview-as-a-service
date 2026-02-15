from django.shortcuts import get_object_or_404, render

from .models import Interviewer, InterviewSubject, Technology


def interviewer_list(request):
    """List all active interviewers with optional filtering."""
    interviewers = Interviewer.objects.filter(is_active=True)

    # Filter by technology
    tech_slug = request.GET.get("technology")
    if tech_slug:
        interviewers = interviewers.filter(technologies__slug=tech_slug)

    # Filter by subject
    subject_slug = request.GET.get("subject")
    if subject_slug:
        interviewers = interviewers.filter(subjects__slug=subject_slug)

    technologies = Technology.objects.all()
    subjects = InterviewSubject.objects.all()

    # For HTMX partial requests, return just the grid
    if request.headers.get("HX-Request"):
        return render(
            request,
            "interviewers/partials/grid.html",
            {"interviewers": interviewers},
        )

    return render(
        request,
        "interviewers/list.html",
        {
            "interviewers": interviewers,
            "technologies": technologies,
            "subjects": subjects,
            "selected_tech": tech_slug,
            "selected_subject": subject_slug,
        },
    )


def featured_interviewers(request):
    """Return featured interviewers for HTMX partial load."""
    interviewers = Interviewer.objects.filter(is_active=True)[:6]
    return render(
        request,
        "interviewers/partials/grid.html",
        {"interviewers": interviewers},
    )


def interviewer_detail_modal(request, pk):
    """Return interviewer detail modal for HTMX."""
    interviewer = get_object_or_404(Interviewer, pk=pk, is_active=True)
    return render(
        request,
        "interviewers/detail_modal.html",
        {"interviewer": interviewer},
    )
