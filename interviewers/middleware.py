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
