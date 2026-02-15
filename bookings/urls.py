from django.urls import path

from . import views, webhooks

app_name = "bookings"

urlpatterns = [
    path("<int:interviewer_id>/", views.booking_start, name="start"),
    path("<int:interviewer_id>/form/", views.booking_form, name="form"),
    path("<int:interviewer_id>/create/", views.create_booking, name="create"),
    path("success/", views.checkout_success, name="success"),
    path("cancel/", views.checkout_cancel, name="cancel"),
    path("webhook/stripe/", webhooks.stripe_webhook, name="stripe_webhook"),
]
