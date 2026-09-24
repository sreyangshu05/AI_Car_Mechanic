from rest_framework.views import APIView
from rest_framework.response import Response
from conversations.models import Conversation
from core.exceptions import error_response
from .models import Diagnosis
from services.ai_service import generate_diagnosis

class DiagnosisView(APIView):
    def post(self, request):
        try: conversation = Conversation.objects.get(id=request.data.get('conversation_id'))
        except (Conversation.DoesNotExist, ValueError, TypeError): return error_response('NOT_FOUND', 'Conversation not found.', 404)
        user_text = ' '.join(conversation.messages.filter(role='user').values_list('content', flat=True))
        media_ids = request.data.get('media_ids', []) or []
        if not isinstance(media_ids, list) or any(not isinstance(item, int) for item in media_ids):
            return error_response('VALIDATION_ERROR', 'media_ids must be an array of integers.')
        attached_media = conversation.media_files.filter(id__in=media_ids)
        if media_ids and attached_media.count() != len(set(media_ids)):
            return error_response('INVALID_MEDIA', 'One or more media files do not belong to this conversation.', 400)
        if attached_media.exists():
            user_text += '\nAttached media available for inspection: ' + ', '.join(f'{item.file_type} upload' for item in attached_media) + '.'
        if len(user_text.split()) < 4: return error_response('INSUFFICIENT_DATA', 'Please provide a little more detail about the symptom.')
        text = user_text.lower()
        if any(x in text for x in ('brake', 'steering', 'fuel leak', 'heavy smoke', 'burning')):
            issue, severity, action = 'Possible safety-critical fault', 'high', 'Do not continue driving if unsafe; arrange professional inspection or roadside assistance.'
            causes = ['Component wear or failure', 'Fluid, electrical, or mechanical fault']
        elif any(x in text for x in ('overheat', 'overheating', 'temperature', 'steam')):
            issue, severity, action = 'Possible cooling-system problem', 'high', 'Stop safely if the temperature is high or steam is visible. Allow the engine to cool and arrange inspection.'
            causes = ['Low coolant or leak', 'Thermostat, fan, or water-pump fault']
        elif any(x in text for x in ("won't start", 'wont start', 'clicking', 'crank')):
            issue, severity, action = 'Possible battery, connection, or starter issue', 'medium', 'Have the battery, terminals, and starting circuit tested before replacing parts.'
            causes = ['Weak battery', 'Loose connection', 'Starter-system fault']
        else:
            issue, severity, action = 'Possible issue requiring professional inspection', 'medium', 'Avoid unsafe driving if symptoms worsen and arrange a qualified mechanic inspection.'
            causes = ['More information and an in-person inspection are needed']
        ai_result = generate_diagnosis(user_text)
        if ai_result:
            issue, causes, severity = ai_result['probable_issue'], ai_result['possible_causes'], ai_result['severity']
            action, confidence = ai_result['recommended_action'], ai_result['confidence']
        else:
            confidence = 0.55
        diagnosis = Diagnosis.objects.create(conversation=conversation, summary='This is a preliminary assessment, not a confirmed diagnosis.', probable_issue=issue, possible_causes=causes, severity=severity, recommended_action=action, confidence=confidence)
        conversation.status = 'diagnosed'; conversation.save(update_fields=['status', 'updated_at'])
        return Response({'diagnosis_id': diagnosis.id, 'summary': diagnosis.summary, 'probable_issue': issue, 'possible_causes': causes, 'severity': diagnosis.severity, 'recommended_action': action, 'confidence': float(diagnosis.confidence), 'booking_available': True})
