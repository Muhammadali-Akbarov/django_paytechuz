"""
Atmos payment API views for payment link based transactions.
"""

import logging


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AtmosWebhookSerializer
from .services import AtmosAPIError, AtmosService

logger = logging.getLogger(__name__)


class AtmosWebhookAPIView(APIView):
    """API view for handling Atmos webhook notifications"""

    def post(self, request):
        """Handle webhook notification from Atmos"""
        print("Webhook received: %s", request.data)
        serializer = AtmosWebhookSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error("Invalid webhook data: %s", serializer.errors)
            return Response({
                'status': 0,
                'message': 'Invalid webhook data'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            atmos_service = AtmosService()

            # Debug log
            logger.info("Webhook received: %s", serializer.validated_data)

            # Verify webhook signature
            received_signature = serializer.validated_data.get('sign', '')
            signature_valid = atmos_service.verify_webhook_signature(
                serializer.validated_data, received_signature)

            if not signature_valid:
                logger.error("Invalid webhook signature")
                return Response({
                    'status': 0,
                    'message': 'Invalid signature'
                }, status=status.HTTP_400_BAD_REQUEST)

            transaction = atmos_service.handle_webhook(
                serializer.validated_data)

            logger.info("Webhook processed for transaction %s",
                        transaction.transaction_id)

            return Response({
                'status': 1,
                'message': 'Успешно'
            }, status=status.HTTP_200_OK)

        except AtmosAPIError as e:
            logger.error("Webhook processing error: %s", str(e))
            return Response({
                'status': 0,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Unexpected webhook error: %s", str(e))
            return Response({
                'status': 0,
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
