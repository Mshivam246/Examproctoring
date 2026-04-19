from django.contrib import admin

from .models import Choice, Exam, ProctorEvent, Question, Submission


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "start_time", "end_time", "duration_minutes", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "id", "marks")
    inlines = [ChoiceInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("exam", "user", "score", "submitted_at")
    list_filter = ("exam",)


@admin.register(ProctorEvent)
class ProctorEventAdmin(admin.ModelAdmin):
    list_display = ("user", "exam", "event_type", "severity", "created_at")
    list_filter = ("event_type", "severity")
