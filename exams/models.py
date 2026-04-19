from django.conf import settings
from django.db import models


class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.exam.title} - Q{self.pk}"


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Choice {self.pk}"


class Submission(models.Model):
    exam = models.ForeignKey(Exam, related_name="submissions", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="submissions", on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)
    answers_json = models.JSONField(default=dict)

    class Meta:
        unique_together = ("exam", "user")

    def __str__(self):
        return f"{self.user} - {self.exam}"


class ProctorEvent(models.Model):
    EVENT_TYPES = [
        ("tab_switch", "Tab Switch"),
        ("window_blur", "Window Blur"),
        ("fullscreen_exit", "Fullscreen Exit"),
        ("multiple_person", "Multiple Persons"),
        ("no_person", "No Person Detected"),
        ("high_noise", "High Noise"),
        ("camera_error", "Camera Error"),
    ]

    exam = models.ForeignKey(Exam, related_name="proctor_events", on_delete=models.CASCADE)
    submission = models.ForeignKey(
        Submission,
        null=True,
        blank=True,
        related_name="proctor_events",
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="proctor_events", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=40, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, default="medium")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} {self.event_type}"
