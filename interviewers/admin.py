from django.contrib import admin

from .emails import send_approval_notification
from .models import HumanLanguage, Interviewer, InterviewSubject, Technology


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


@admin.register(HumanLanguage)
class HumanLanguageAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Interviewer)
class InterviewerAdmin(admin.ModelAdmin):
    list_display = ["display_name", "hourly_rate", "approval_status", "is_active", "created_at"]
    list_filter = ["approval_status", "is_active", "technologies", "subjects", "languages"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "bio"]
    filter_horizontal = ["technologies", "subjects", "languages"]
    readonly_fields = ["created_at", "updated_at", "tos_accepted_version", "tos_accepted_at"]
    actions = ["approve_interviewers"]
    fieldsets = [
        (None, {"fields": ["user", "approval_status", "is_active"]}),
        ("Profile", {"fields": ["bio", "photo", "companies"]}),
        ("Booking", {"fields": ["cal_link", "hourly_rate"]}),
        ("Skills", {"fields": ["technologies", "subjects", "languages"]}),
        ("ToS Acceptance", {"fields": ["tos_accepted_version", "tos_accepted_at"]}),
        ("Timestamps", {"fields": ["created_at", "updated_at"]}),
    ]

    @admin.action(description="Approve selected interviewers")
    def approve_interviewers(self, request, queryset):
        newly_approved = list(queryset.filter(approval_status=Interviewer.ApprovalStatus.PENDING))
        for interviewer in newly_approved:
            interviewer.approval_status = Interviewer.ApprovalStatus.APPROVED
            interviewer.save(update_fields=["approval_status"])
            send_approval_notification(interviewer)

        self.message_user(request, f"Approved {len(newly_approved)} interviewer(s).")
