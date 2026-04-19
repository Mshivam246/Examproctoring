from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Exam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("duration_minutes", models.PositiveIntegerField(default=60)),
                ("total_marks", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField()),
                ("marks", models.PositiveIntegerField(default=1)),
                (
                    "exam",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="exams.exam"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Choice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.CharField(max_length=500)),
                ("is_correct", models.BooleanField(default=False)),
                (
                    "question",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="choices", to="exams.question"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Submission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("score", models.FloatField(default=0)),
                ("answers_json", models.JSONField(default=dict)),
                (
                    "exam",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="exams.exam"),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"unique_together": {("exam", "user")}},
        ),
        migrations.CreateModel(
            name="ProctorEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("tab_switch", "Tab Switch"),
                            ("window_blur", "Window Blur"),
                            ("fullscreen_exit", "Fullscreen Exit"),
                            ("multiple_person", "Multiple Persons"),
                            ("no_person", "No Person Detected"),
                            ("high_noise", "High Noise"),
                            ("camera_error", "Camera Error"),
                        ],
                        max_length=40,
                    ),
                ),
                ("severity", models.CharField(default="medium", max_length=20)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "exam",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="proctor_events", to="exams.exam"),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="proctor_events",
                        to="exams.submission",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="proctor_events", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
