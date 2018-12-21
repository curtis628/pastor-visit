from django.urls import path

from . import views

urlpatterns = [
    path("", views.HouseholdCreateView.as_view(), name="index"),
    path("success", views.SuccessView.as_view(), name="success"),
    path("about", views.AboutView.as_view(), name="about"),
    path("feedback", views.FeedbackCreateView.as_view(), name="feedback"),
    path(
        "feedback/success", views.FeedbackSuccessView.as_view(), name="feedback_success"
    ),
    path("faqs", views.FaqListView.as_view(), name="faqs"),
]
