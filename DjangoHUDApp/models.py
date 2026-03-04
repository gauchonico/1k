from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    bio = models.TextField(blank=True)
    # Track the "Habit" they are flipping (e.g., "Cigarettes", "Betting")
    target_habit = models.CharField(max_length=100, help_text="What habit are you replacing?")
    total_saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_founder = models.BooleanField(default=False)
    current_streak = models.IntegerField(default=0)
    last_contribution_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.total_saved} UGX"
    
class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak_record')
    longest_streak = models.PositiveIntegerField(default=0, help_text="All-time best streak")
    total_days_contributed = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} History (Best: {self.longest_streak})"
    
class SavingGroup(models.Model):
    name = models.CharField(max_length=100, default="The 1k Project")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    daily_requirement = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    members = models.ManyToManyField(User, related_name="savings_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_annual_total(self, year=None):
        if not year:
            year = timezone.now().year
        return Transaction.objects.filter(
            group=self, 
            status='completed', 
            created_at__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0

    @property
    def total_pool(self):
        return Transaction.objects.filter(group=self, status='completed').aggregate(
            total=models.Sum('amount'))['total'] or 0
        
    
        
class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(SavingGroup, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, help_text="Mobile Money ID")
    proof_image = models.ImageField(upload_to='proofs/', blank=True, null=True)
    reference = models.CharField(max_length=100, unique=True) # For Mobile Money/Stripe IDs
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_id}"
        
class PaymentVerification(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='verification')
    verifier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_staff': True})
    screenshot = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verify {self.transaction.reference}"
    
    
class YearlySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField(default=2026)
    total_saved_that_year = models.DecimalField(max_digits=12, decimal_places=2)
    highest_streak_that_year = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'year')
