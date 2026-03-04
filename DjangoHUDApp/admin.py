from django.contrib import admin, messages
from .models import Profile, SavingGroup, Transaction, PaymentVerification, Streak

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # This allows you to see who is a founder and their total savings immediately
    list_display = ('user', 'total_saved', 'current_streak', 'is_founder', 'phone_number')
    list_filter = ('is_founder',)
    search_fields = ('user__username', 'phone_number')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_id', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'user__username')
    actions = ['mark_as_completed'] # Register the action here

    @admin.action(description='Approve selected 1k payments')
    def mark_as_completed(self, request, queryset):
        # We only want to process pending transactions to avoid double-counting
        pending_txns = queryset.filter(status='pending')
        count = pending_txns.count()
        
        for txn in pending_txns:
            txn.status = 'completed'
            txn.save() # This save() triggers the Signal to update Profile & Streak
            
        self.message_user(
            request, 
            f"Successfully approved {count} payments. Balances and streaks updated!",
            messages.SUCCESS  
        )

@admin.register(SavingGroup)
class SavingGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at')

@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'longest_streak', 'total_days_contributed')

@admin.register(PaymentVerification)
class PaymentVerificationAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'verifier', 'verified_at')