"""Atmos payment models for payment link based transactions"""
from django.db import models
from django.utils import timezone


class AtmosTransaction(models.Model):
    """Model for Atmos payment link based transactions"""

    STATUS_CHOICES = [
        ('created', 'Created'),
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    # Basic transaction info
    transaction_id = models.BigIntegerField(unique=True, null=True, blank=True)
    account = models.CharField(
        max_length=255,
        help_text="Order ID or account identifier"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Transaction status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='created'
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'atmos_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return (f"Atmos Transaction {self.transaction_id} - "
                f"{self.amount} som - {self.status}")
