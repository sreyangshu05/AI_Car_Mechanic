from django.db import models
from conversations.models import Conversation
from core.constants import SEVERITY_CHOICES
class Diagnosis(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='diagnoses')
    summary = models.TextField()
    probable_issue = models.CharField(max_length=255)
    possible_causes = models.JSONField(default=list)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    recommended_action = models.TextField()
    confidence = models.DecimalField(max_digits=4, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
