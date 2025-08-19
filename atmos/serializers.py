"""
Serializers for Atmos payment link based transactions.
"""

from rest_framework import serializers

from .models import AtmosTransaction


class AtmosWebhookSerializer(serializers.Serializer):
    """Serializer for Atmos webhook data"""

    store_id = serializers.CharField()
    transaction_id = serializers.IntegerField()
    transaction_time = serializers.CharField()
    amount = serializers.IntegerField()  # Amount in tiyin
    invoice = serializers.CharField()  # Our account field
    sign = serializers.CharField()  # Digital signature

    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class AtmosTransactionSerializer(serializers.ModelSerializer):
    """Serializer for AtmosTransaction model"""

    class Meta:
        model = AtmosTransaction
        fields = [
            'id', 'transaction_id', 'account', 'amount',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'created_at', 'updated_at'
        ]
