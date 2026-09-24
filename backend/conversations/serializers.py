"""Serializers for conversation and chat API."""

from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for individual messages."""

    media_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'role', 'content', 'message_type', 'created_at', 'media_url',
        ]
        read_only_fields = ['id', 'created_at']

    def get_media_url(self, obj):
        """Get the URL of attached media, if any."""
        media = obj.media_files.first()
        if media and media.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(media.file.url)
            return media.file.url
        return None


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversation with nested messages."""

    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'status', 'vehicle_info', 'created_at', 'updated_at', 'messages',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatRequestSerializer(serializers.Serializer):
    """Validates incoming chat messages."""

    conversation_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(
        required=True,
        min_length=1,
        max_length=5000,
        error_messages={
            'blank': 'Message cannot be empty.',
            'required': 'Message is required.',
            'min_length': 'Message cannot be empty.',
            'max_length': 'Message is too long (max 5000 characters).',
        },
    )
    media_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
    )

    def validate_message(self, value):
        """Strip whitespace and validate non-empty."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Message cannot be empty.')
        return value


class ChatResponseSerializer(serializers.Serializer):
    """Structures the chat API response."""

    conversation_id = serializers.UUIDField()
    reply = serializers.CharField()
    status = serializers.CharField()
    diagnosis_ready = serializers.BooleanField()

