import uuid

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from apps.accounts.models import Organisation, Role


class Command(BaseCommand):
    help = "Bootstrap an organisation + an ORGADMIN (or SUPERADMIN) user."

    def add_arguments(self, parser):
        parser.add_argument("--org-name", required=True)
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--email", default="")
        parser.add_argument("--role", choices=[Role.ORGADMIN, Role.SUPERADMIN], default=Role.ORGADMIN)

    def handle(self, *args, **options):
        org_name = options["org_name"].strip()
        username = options["username"].strip()
        password = options["password"]
        email = options["email"].strip()
        role = options["role"]

        if not org_name:
            raise CommandError("--org-name is required")
        if not username:
            raise CommandError("--username is required")
        if not password:
            raise CommandError("--password is required")

        org, created = Organisation.objects.get_or_create(name=org_name)

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise CommandError("username already exists: %s" % username)

        is_staff = True
        is_superuser = role == Role.SUPERADMIN

        user = User.objects.create_user(
            username=username,
            email=email,
            organisation=org,
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS("Organisation: %s (%s)" % (org.name, org.id)))
        self.stdout.write(self.style.SUCCESS("User: %s (%s) role=%s" % (user.username, user.id, user.role)))

