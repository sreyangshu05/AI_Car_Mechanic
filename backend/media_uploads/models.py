from django.db import models
from conversations.models import Conversation, Message

class MediaFile(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='media_files')
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='media_files')
    file = models.FileField(upload_to='car-media/%Y/%m/')
    file_type = models.CharField(max_length=10)
    file_size = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
