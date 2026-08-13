from django.shortcuts import redirect
from django.urls import reverse


class TosAcceptanceMiddleware:
    """Gate the interviewer dashboard behind ToS acceptance.

    Redirects a logged-in interviewer to the accept-ToS page whenever their
    accepted version doesn't match interviewers.models.CURRENT_TOS_VERSION
    (never accepted, or we've since bumped the version).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard/"):
            user = request.user
            interviewer = getattr(user, "interviewer", None) if user.is_authenticated else None
            if interviewer and not interviewer.has_accepted_current_tos:
                accept_url = reverse("accounts:accept_tos")
                if request.path != accept_url:
                    return redirect(f"{accept_url}?next={request.path}")

        return self.get_response(request)


class ApprovalRequiredMiddleware:
    """Block the interviewer dashboard until an admin approves the account.

    Self-registered interviewers can log in immediately but shouldn't get
    any real functionality until interviewers.models.Interviewer.approval_status
    is flipped to approved from Django admin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard/"):
            user = request.user
            interviewer = getattr(user, "interviewer", None) if user.is_authenticated else None
            if interviewer and not interviewer.is_approved:
                pending_url = reverse("accounts:pending_approval")
                if request.path != pending_url:
                    return redirect(pending_url)

        return self.get_response(request)
