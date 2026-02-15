from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_name",
        "interviewer",
        "scheduled_at",
        "status",
        "created_at",
    ]
    list_filter = ["status", "interviewer", "scheduled_at"]
    search_fields = ["customer_name", "customer_email", "interviewer__user__username"]
    readonly_fields = [
        "stripe_payment_intent_id",
        "stripe_checkout_session_id",
        "cal_booking_uid",
        "created_at",
        "updated_at",
    ]
    fieldsets = [
        (None, {"fields": ["interviewer", "status"]}),
        (
            "Customer Info",
            {
                "fields": [
                    "customer_name",
                    "customer_email",
                    "customer_background",
                    "interview_focus",
                    "target_companies",
                    "additional_info",
                    "resume",
                ]
            },
        ),
        ("Scheduling", {"fields": ["scheduled_at", "duration_minutes", "cal_booking_uid"]}),
        (
            "Payment",
            {"fields": ["stripe_checkout_session_id", "stripe_payment_intent_id"]},
        ),
        ("Timestamps", {"fields": ["created_at", "updated_at"]}),
    ]
