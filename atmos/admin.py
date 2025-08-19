"""
Admin configuration for Atmos payment app.
"""

from django.contrib import admin
from .models import AtmosTransaction


@admin.register(AtmosTransaction)
class AtmosTransactionAdmin(admin.ModelAdmin):
    """Admin interface for Atmos transactions"""

    list_display = [
        'transaction_id', 'account', 'amount', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['transaction_id', 'account']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
