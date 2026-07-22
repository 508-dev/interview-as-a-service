from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("profile/", views.profile_edit, name="profile"),
    path("profile/password/", views.password_change, name="password_change"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("bookings/<int:pk>/complete/", views.booking_complete, name="booking_complete"),
]
