from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from datetime import datetime, timezone as py_timezone # Use Python's built-in timezone
from django.utils import timezone as django_timezone # Keep this for Django-specific logic
from DjangoHUDApp.models import Profile, Streak, SavingGroup, Transaction

class Command(BaseCommand):
    help = 'Imports the 17 founding members with historical 2025 data'

    def handle(self, *args, **options):
        members_data = [
            ("jason_k", 110000), ("trish", 360000), ("sean", 370000),
            ("isaac", 152000), ("wanz_niko", 98000), ("balam_k", 5000),
            ("izati", 94500), ("gaucho", 310000), ("alvin", 18000),
            ("alex", 32000), ("sulei_kuda", 317000), ("micheal_builder", 135000),
            ("buk", 10000), ("bantu", 262000), ("alvin_sabiti", 34000),
            ("adrian", 272000), ("gab", 50000)
        ]

        group, _ = SavingGroup.objects.get_or_create(name="The 1k Project")
        last_year_end = datetime(2025, 12, 31, 23, 59, tzinfo=py_timezone.utc)

        for username, amount in members_data:
            clean_username = username.lower().replace(" ", "_")
            user, created = User.objects.get_or_create(username=clean_username)
            
            if created:
                user.set_password("StartSaving2026")
                user.save()
            
            group.members.add(user)

            # Access the profile created by your signal and set the founder badge
            profile = user.profile
            profile.is_founder = True
            profile.save()

            # Create the 2025 'Seed' Transaction
            txn, txn_created = Transaction.objects.get_or_create(
                user=user,
                group=group,
                amount=amount,
                transaction_id=f"2025_TOTAL_{clean_username}",
                defaults={
                    'status': 'completed',
                    'reference': f"LEGACY_2025_{clean_username}",
                }
            )
            
            if txn_created:
                Transaction.objects.filter(pk=txn.pk).update(created_at=last_year_end)

            self.stdout.write(self.style.SUCCESS(f'Successfully seeded 2025 data and founder badge for {username}'))