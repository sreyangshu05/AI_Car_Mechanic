from datetime import date, time
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from conversations.models import Conversation
from diagnosis.models import Diagnosis
from core.exceptions import error_response
from .models import Booking

FIELDS = ('conversation_id','diagnosis_id','customer_name','phone','email','vehicle_make','vehicle_model','vehicle_year','problem_summary','preferred_date','preferred_time')
class BookingCreateView(APIView):
    def post(self, request):
        data = request.data
        missing = [f for f in FIELDS if not data.get(f)]
        if missing: return error_response('VALIDATION_ERROR', 'Missing required fields: ' + ', '.join(missing))
        try:
            conversation = Conversation.objects.get(id=data['conversation_id']); diagnosis = Diagnosis.objects.get(id=data['diagnosis_id'], conversation=conversation)
            preferred_date = date.fromisoformat(str(data['preferred_date']))
            preferred_time = time.fromisoformat(str(data['preferred_time']))
            year = int(data['vehicle_year'])
        except (Conversation.DoesNotExist, Diagnosis.DoesNotExist): return error_response('NOT_FOUND', 'Conversation or diagnosis not found.', 404)
        except (ValueError, TypeError): return error_response('VALIDATION_ERROR', 'Use valid vehicle year, ISO date, and time values.')
        if preferred_date < date.today(): return error_response('VALIDATION_ERROR', 'Preferred date cannot be in the past.')
        try: validate_email(str(data['email']).strip())
        except ValidationError: return error_response('VALIDATION_ERROR', 'Enter a valid email address.')
        phone = str(data['phone']).strip()
        if not re.fullmatch(r'\+?[0-9 ()-]{7,20}', phone): return error_response('VALIDATION_ERROR', 'Enter a valid phone number.')
        if year < 1886 or year > date.today().year + 1: return error_response('VALIDATION_ERROR', 'Enter a valid vehicle year.')
        if Booking.objects.filter(conversation=conversation, diagnosis=diagnosis, status__in=('pending','confirmed')).exists(): return error_response('DUPLICATE_BOOKING', 'A booking already exists for this diagnosis.', 409)
        booking = Booking.objects.create(conversation=conversation, diagnosis=diagnosis, customer_name=str(data['customer_name']).strip(), phone=phone, email=str(data['email']).strip(), vehicle_make=str(data['vehicle_make']).strip(), vehicle_model=str(data['vehicle_model']).strip(), vehicle_year=year, problem_summary=str(data['problem_summary']).strip(), preferred_date=preferred_date, preferred_time=preferred_time)
        conversation.status = 'booked'; conversation.save(update_fields=['status','updated_at'])
        return Response({'id': booking.id, 'status': booking.status, 'customer_name': booking.customer_name, 'vehicle': f'{booking.vehicle_make} {booking.vehicle_model} {booking.vehicle_year}', 'problem_summary': booking.problem_summary, 'preferred_date': booking.preferred_date, 'preferred_time': booking.preferred_time}, status=201)
class BookingDetailView(APIView):
    def get(self, request, booking_id):
        try: b = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist: return error_response('NOT_FOUND', 'Booking not found.', 404)
        return Response({'id': b.id, 'status': b.status, 'customer_name': b.customer_name, 'vehicle': f'{b.vehicle_make} {b.vehicle_model} {b.vehicle_year}', 'problem_summary': b.problem_summary, 'preferred_date': b.preferred_date, 'preferred_time': b.preferred_time})
