from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Transaction, Streak, Profile
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_dependencies(sender, instance, created, **kwargs):
    """Ensure every new user has a Profile and a Streak record immediately."""
    if created:
        # Check if they exist first to avoid errors during bulk imports
        Profile.objects.get_or_create(user=instance)
        Streak.objects.get_or_create(user=instance)

@receiver(post_save, sender=Transaction)
def process_savings_logic(sender, instance, **kwargs):
    """
    Triggered when an admin updates Transaction status to 'completed'.
    Updates the Profile balance and the Streak logic.
    """
    if instance.status == 'completed':
        profile = instance.user.profile
        streak_record = instance.user.streak_record
        
        # 1. Update Total Saved
        profile.total_saved += instance.amount
        
        # 2. Calculate Streak Logic
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        if profile.last_contribution_date == yesterday:
            # Consistent saving - increment
            profile.current_streak += 1
        elif profile.last_contribution_date == today:
            # Already saved today, don't increment streak twice
            pass
        else:
            # Gap in saving - reset to 1
            profile.current_streak = 1
            
        # 3. Update Longest Streak in the Streak Model
        if profile.current_streak > streak_record.longest_streak:
            streak_record.longest_streak = profile.current_streak
            
        # Save everything
        profile.last_contribution_date = today
        profile.save()
        streak_record.total_days_contributed += 1
        streak_record.save()