from datetime import timedelta

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Insert dummy rows into Django auth, session, and admin log tables."

    def handle(self, *args, **options):
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "Django",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write("Created superuser admin / admin123")

        demo_users = [
            ("alice", "alice@example.com", "Alice", "Anderson"),
            ("bob", "bob@example.com", "Bob", "Baker"),
            ("carol", "carol@example.com", "Carol", "Clark"),
        ]
        users = [admin_user]
        for username, email, first, last in demo_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "is_staff": username == "alice",
                },
            )
            if created:
                user.set_password("password123")
                user.save()
            users.append(user)

        editors, _ = Group.objects.get_or_create(name="Editors")
        viewers, _ = Group.objects.get_or_create(name="Viewers")
        editors.permissions.set(
            Permission.objects.filter(codename__in=["add_user", "change_user", "view_user"])[:3]
        )
        viewers.permissions.set(
            Permission.objects.filter(codename__in=["view_user", "view_group"])[:2]
        )

        alice = User.objects.get(username="alice")
        bob = User.objects.get(username="bob")
        alice.groups.set([editors])
        bob.groups.set([viewers])
        admin_user.user_permissions.add(
            *Permission.objects.filter(content_type__app_label="auth", codename="view_group")[:1]
        )

        user_ct = ContentType.objects.get_for_model(User)
        group_ct = ContentType.objects.get_for_model(Group)
        now = timezone.now()

        log_specs = [
            (ADDITION, user_ct, alice.pk, "Added demo user alice"),
            (CHANGE, user_ct, bob.pk, "Updated bob profile"),
            (DELETION, group_ct, viewers.pk, "Reviewed viewers group"),
        ]
        for action, ct, obj_pk, message in log_specs:
            LogEntry.objects.get_or_create(
                user=admin_user,
                content_type=ct,
                object_id=str(obj_pk),
                object_repr=message[:200],
                action_flag=action,
                change_message=message,
                action_time=now - timedelta(minutes=action * 5),
            )

        for user in users:
            store = SessionStore()
            store.create()
            store["_auth_user_id"] = str(user.pk)
            store["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
            store.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded: {User.objects.count()} users, "
                f"{Group.objects.count()} groups, "
                f"{LogEntry.objects.count()} admin log rows, "
                f"{Session.objects.count()} sessions."
            )
        )