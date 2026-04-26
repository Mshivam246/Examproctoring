from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a superuser from environment variables."

    def handle(self, *args, **options):
        import os

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping admin bootstrap because DJANGO_SUPERUSER_USERNAME, "
                    "DJANGO_SUPERUSER_EMAIL, or DJANGO_SUPERUSER_PASSWORD is missing."
                )
            )
            return

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        updated = False
        if user.email != email:
            user.email = email
            updated = True
        if not user.is_staff:
            user.is_staff = True
            updated = True
        if not user.is_superuser:
            user.is_superuser = True
            updated = True

        user.set_password(password)
        updated = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
        elif updated:
            self.stdout.write(self.style.SUCCESS(f"Updated superuser '{username}'."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already configured."))
