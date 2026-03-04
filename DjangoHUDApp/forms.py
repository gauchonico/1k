from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_id', 'reference']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg rounded-pill',
                'placeholder': 'e.g. 1000'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control rounded-pill',
                'placeholder': 'Mobile Money Reference'
            }),
            'reference': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional note...'
            }),
        }