from django.contrib import admin

from .models import Interviewer, InterviewSubject, Technology


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(InterviewSubject)
class InterviewSubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Interviewer)
class InterviewerAdmin(admin.ModelAdmin):
    list_display = ["display_name", "hourly_rate", "is_active", "created_at"]
    list_filter = ["is_active", "technologies", "subjects"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "bio"]
    filter_horizontal = ["technologies", "subjects"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["user", "is_active"]}),
        ("Profile", {"fields": ["bio", "photo", "companies"]}),
        ("Booking", {"fields": ["cal_event_type_id", "hourly_rate"]}),
        ("Skills", {"fields": ["technologies", "subjects"]}),
        ("Timestamps", {"fields": ["created_at", "updated_at"]}),
    ]
