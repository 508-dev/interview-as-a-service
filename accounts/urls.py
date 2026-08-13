from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("pending-approval/", views.pending_approval_view, name="pending_approval"),
    path("accept-tos/", views.accept_tos_view, name="accept_tos"),
]
