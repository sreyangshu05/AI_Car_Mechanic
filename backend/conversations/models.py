"""Database models for conversations and messages."""

import uuid
from django.db import models
from core.constants import (
    CONVERSATION_STATUS_CHOICES,
    MESSAGE_ROLE_CHOICES,
    MESSAGE_TYPE_CHOICES,
)


class Conversation(models.Model):
    """A troubleshooting conversation session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=CONVERSATION_STATUS_CHOICES,
        default='active',
        db_index=True,
    )
    vehicle_info = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Conversation {self.id} ({self.status})'

    @property
    def message_count(self):
        return self.messages.count()

    @property
    def user_message_count(self):
        return self.messages.filter(role='user').count()


class Message(models.Model):
    """A single message within a conversation."""

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=10, choices=MESSAGE_ROLE_CHOICES)
    content = models.TextField()
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='text',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f'{self.role}: {preview}'

