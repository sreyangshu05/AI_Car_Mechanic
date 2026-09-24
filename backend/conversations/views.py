"""Views for chat and conversation history APIs."""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.exceptions import NotFoundError, error_response
from .models import Conversation
from .serializers import (
    ChatRequestSerializer,
    ConversationSerializer,
)
from services.conversation_service import process_message, is_car_related

logger = logging.getLogger(__name__)

# Polite redirect message for non-car queries (no AI call needed)
OFF_TOPIC_REPLY = (
    "I'm your virtual car mechanic, so I can help with vehicle troubleshooting, "
    "maintenance, diagnostics, or repair-related questions. "
    "What issue are you experiencing with your car?"
)


class ChatView(APIView):
    """
    POST /api/chat/
    Send a user message and receive an AI-powered mechanic response.
    Uses deterministic domain filtering before calling Gemini.
    """

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            errors = []
            for field, msgs in serializer.errors.items():
                for msg in msgs:
                    errors.append(str(msg))
            return error_response(
                'VALIDATION_ERROR',
                '; '.join(errors),
                400,
            )

        message = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')
        media_ids = serializer.validated_data.get('media_ids', [])

        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return error_response('NOT_FOUND', 'Conversation not found.', 404)
        else:
            conversation = Conversation.objects.create()

        # Deterministic domain check — no AI call for obvious non-car queries
        if not is_car_related(message, conversation):
            # Save messages but don't waste an AI call
            conversation.messages.create(
                role='user', content=message, message_type='text',
            )
            conversation.messages.create(
                role='assistant', content=OFF_TOPIC_REPLY, message_type='text',
            )
            return Response({
                'conversation_id': str(conversation.id),
                'reply': OFF_TOPIC_REPLY,
                'status': 'off_topic',
                'diagnosis_ready': False,
            })

        # Delegate to conversation service (may call Gemini)
        try:
            result = process_message(conversation, message, media_ids)
        except Exception as e:
            logger.error('Chat processing error: %s', str(e), exc_info=True)
            fallback_reply = (
                "I'm having a bit of trouble processing that right now. "
                "Could you try describing your car issue again?"
            )
            # Still save the user message
            conversation.messages.create(
                role='user', content=message, message_type='text',
            )
            conversation.messages.create(
                role='assistant', content=fallback_reply, message_type='text',
            )
            return Response({
                'conversation_id': str(conversation.id),
                'reply': fallback_reply,
                'status': 'error',
                'diagnosis_ready': False,
            })

        return Response({
            'conversation_id': str(conversation.id),
            'reply': result['reply'],
            'status': result.get('status', 'follow_up'),
            'diagnosis_ready': result.get('diagnosis_ready', False),
        })


class ConversationDetailView(APIView):
    """
    GET /api/conversations/{id}/
    Retrieve conversation history with all messages.
    """

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise NotFoundError('Conversation not found.')

        serializer = ConversationSerializer(
            conversation, context={'request': request},
        )
        return Response(serializer.data)
