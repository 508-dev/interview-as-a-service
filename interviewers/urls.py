from django.urls import path

from . import views

app_name = "interviewers"

urlpatterns = [
    path("", views.interviewer_list, name="list"),
    path("featured/", views.featured_interviewers, name="featured"),
    path("<int:pk>/modal/", views.interviewer_detail_modal, name="detail_modal"),
]
