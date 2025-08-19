"""
Atmos payment service for payment link based transactions.
"""

import base64
import hashlib
from decimal import Decimal
from typing import Dict, Any

import requests
from django.conf import settings

from .models import AtmosTransaction


class AtmosAPIError(Exception):
    """Custom exception for Atmos API errors"""


class AtmosService:
    """Service for Atmos payment link based transactions"""

    def __init__(self):
        self.config = getattr(settings, 'ATMOS', {})
        self.base_url = 'https://partner.atmos.uz'
        self.consumer_key = self.config.get('CONSUMER_KEY', '')
        self.consumer_secret = self.config.get('CONSUMER_SECRET', '')
        self.store_id = self.config.get('STORE_ID', '')
        self.terminal_id = self.config.get('TERMINAL_ID', '')
        self.is_test_mode = self.config.get('IS_TEST_MODE', True)
        self._access_token = None

    def _get_auth_header(self) -> str:
        """Generate Basic Auth header"""
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _get_access_token(self) -> str:
        """Get access token from Atmos"""
        if self._access_token:
            return self._access_token

        url = f"{self.base_url}/token"
        headers = {
            'Authorization': self._get_auth_header(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}

        response = requests.post(url, headers=headers, data=data, timeout=30)

        if response.status_code != 200:
            raise AtmosAPIError(f"Token error: {response.text}")

        token_data = response.json()
        self._access_token = token_data['access_token']
        return self._access_token

    def _make_request(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make API request to Atmos"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f"Bearer {self._get_access_token()}",
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code not in [200, 201]:
            raise AtmosAPIError(f"API error: {response.text}")

        return response.json()

    def create_payment_link(self, amount: Decimal,
                           account: str) -> AtmosTransaction:
        """Create payment transaction and return payment link"""

        # Convert amount to tiyin (multiply by 100)
        amount_tiyin = int(amount * 100)

        # Create transaction in Atmos
        create_data = {
            'amount': amount_tiyin,
            'account': account,
            'store_id': self.store_id,
            'lang': 'ru'
        }

        if self.terminal_id:
            create_data['terminal_id'] = self.terminal_id

        create_response = self._make_request('/merchant/pay/create',
                                           create_data)
        transaction_id = create_response['transaction_id']
        print(create_response)

        # Generate payment URL
        if self.is_test_mode:
            base_url = "https://test-checkout.pays.uz/invoice/get"
            payment_url = (f"{base_url}?storeId={self.store_id}"
                          f"&transactionId={transaction_id}")
        else:
            base_url = "https://checkout.pays.uz/invoice/get"
            payment_url = (f"{base_url}?storeId={self.store_id}"
                          f"&transactionId={transaction_id}")

        # Create local transaction record
        transaction = AtmosTransaction.objects.create(
            transaction_id=transaction_id,
            account=account,
            amount=amount,
            status='created'
        )

        # Store payment URL separately (not in model)
        transaction.payment_url = payment_url

        return transaction

    def verify_webhook_signature(self, webhook_data: Dict,
                                 received_signature: str) -> bool:
        """Verify webhook signature from Atmos"""
        # API key for signature verification from config
        api_key = self.config.get('API_KEY', '')

        # Extract data from webhook
        store_id = str(webhook_data.get('store_id', ''))
        transaction_id = str(webhook_data.get('transaction_id', ''))
        invoice = str(webhook_data.get('invoice', ''))
        amount = str(webhook_data.get('amount', ''))

        # Create signature string: store_id+transaction_id+invoice+amount+api_key
        signature_string = (f"{store_id}{transaction_id}{invoice}"
                            f"{amount}{api_key}")

        # Generate MD5 hash
        calculated_signature = hashlib.md5(
            signature_string.encode('utf-8')).hexdigest()

        # Compare signatures
        return calculated_signature == received_signature

    def handle_webhook(self, webhook_data: Dict) -> AtmosTransaction:
        """Handle webhook notification from Atmos"""

        webhook_transaction_id = webhook_data.get('transaction_id')
        # This is our account field (Order ID)
        invoice = webhook_data.get('invoice')

        try:
            # Find transaction by invoice (account) only
            transaction = AtmosTransaction.objects.get(account=invoice)

            # Update transaction with webhook data
            # Update with new transaction ID from webhook
            transaction.transaction_id = webhook_transaction_id
            transaction.status = 'paid'
            transaction.save()

            # Update related Order status
            self._update_order_status(invoice)

            return transaction

        except AtmosTransaction.DoesNotExist:
            raise AtmosAPIError(
                f"Transaction not found for invoice: {invoice}")

    def _update_order_status(self, order_id: str):
        """Update Order status when payment is completed"""
        try:
            from shop.models import Order
            order = Order.objects.get(id=int(order_id))
            order.status = 'paid'
            order.save()
        except (Order.DoesNotExist, ValueError):
            # Order not found or invalid ID, but don't fail the webhook
            pass
