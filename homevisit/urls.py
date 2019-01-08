from django.urls import path

from . import views

urlpatterns = [
    path("", views.HouseholdCreateView.as_view(), name="index"),
    path("success", views.SuccessView.as_view(), name="success"),
    path("about", views.AboutView.as_view(), name="about"),
    path("contact", views.ContactUsCreateView.as_view(), name="contact"),
    path("contact/success", views.ContactUsSuccessView.as_view(), name="contact_success"),
    path("faqs", views.FaqListView.as_view(), name="faqs"),
]
