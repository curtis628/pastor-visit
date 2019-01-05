from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import Household, Person, Meeting, Faq, Feedback


class PersonInline(admin.TabularInline):
    model = Person
    exclude = ["notes"]
    extra = 0
    verbose_name_plural = "Owner"


class MeetingInline(admin.TabularInline):
    model = Meeting
    exclude = ["notes"]
    extra = 0


class HouseholdAdmin(admin.ModelAdmin):
    fields = ["address"]
    inlines = [PersonInline, MeetingInline]
    list_display = ("address", "owner_name", "upcoming_meeting", "created_date")
    list_filter = ["created_date"]
    search_fields = ["address", "person__first_name", "person__last_name"]
    ordering = ["meeting__start"]


class MeetingAdmin(admin.ModelAdmin):
    model = Meeting
    fields = ["name", "start", "end", "reserved", "household"]
    list_display = ("full_name", "owner_name", "reserved", "household")
    list_filter = ["start", "reserved"]
    ordering = ["start"]


class FeedbackAdmin(admin.ModelAdmin):
    model = Feedback
    fields = ["name", "email", "phone_number", "issue", "feedback", "responded"]
    list_display = (
        "__str__",
        "email",
        "phone_number",
        "created_date",
        "issue",
        "responded",
    )
    list_filter = ["created_date", "responded"]
    ordering = ["-created_date"]
    readonly_fields = ("issue", "feedback")


class FaqAdmin(admin.ModelAdmin):
    model = Feedback
    fields = ["short_name", "question", "answer"]
    list_display = ("question", "created_date")
    list_filter = ["created_date"]
    ordering = ["-created_date"]


admin.site.register(Household, HouseholdAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Faq, FaqAdmin)

# No need for User/Group management on our admin site
admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.site_header = "Homevisits Administration"
