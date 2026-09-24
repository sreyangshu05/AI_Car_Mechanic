from django.db import models
from conversations.models import Conversation
from diagnosis.models import Diagnosis
from core.constants import BOOKING_STATUS_CHOICES
class Booking(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.PROTECT, related_name='bookings')
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.PROTECT, related_name='bookings')
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    vehicle_make = models.CharField(max_length=60)
    vehicle_model = models.CharField(max_length=60)
    vehicle_year = models.PositiveIntegerField()
    problem_summary = models.TextField(max_length=2000)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    status = models.CharField(max_length=12, choices=BOOKING_STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
