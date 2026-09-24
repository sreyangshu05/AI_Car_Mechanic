import re

from core.constants import CAR_KEYWORDS


def is_car_related(text, conversation=None):
    words = set(re.findall(r"[a-z0-9']+", text.lower()))
    return bool(words & CAR_KEYWORDS) or bool(conversation and conversation.messages.filter(role='user').exists())


def _vehicle_info_gaps(text):
    lowered = text.lower()
    words = set(re.findall(r'[a-z]+', lowered))
    makes = {
        'honda', 'toyota', 'ford', 'chevrolet', 'chevy', 'nissan', 'hyundai',
        'kia', 'bmw', 'mercedes', 'audi', 'volkswagen', 'vw', 'subaru', 'mazda',
        'lexus', 'jeep', 'tesla', 'volvo', 'dodge', 'mitsubishi', 'suzuki',
        'tata', 'mahindra', 'maruti',
    }
    gaps = []
    if not re.search(r'\b(?:19|20)\d{2}\b', lowered):
        gaps.append('year')
    if not words.intersection(makes):
        gaps.append('make')
    if not re.search(r'\bmodel\s*[:=-]?\s*[a-z0-9-]+', lowered):
        gaps.append('model')
    if not re.search(r'\b(?:warning|dashboard|check engine|no lights|no warning|light is on|lights are|indicator)\b', lowered):
        gaps.append('whether any dashboard warning lights are on')
    return gaps


def process_message(conversation, message, media_ids=None):
    user_message = conversation.messages.create(role='user', content=message)
    if media_ids:
        from media_uploads.models import MediaFile
        media = list(MediaFile.objects.filter(id__in=media_ids, conversation=conversation))
        if media:
            user_message.message_type = media[0].file_type
            user_message.save(update_fields=['message_type'])
            for item in media:
                item.message = user_message
                item.save(update_fields=['message'])

    lowered = message.lower()
    full_context = ' '.join(conversation.messages.filter(role='user').values_list('content', flat=True))
    if any(x in lowered for x in ('start', 'crank', 'clicking', "won't start", 'wont start')):
        reply = 'When you try to start it, does the engine crank, do you only hear clicking, or is there no sound? Do the dashboard lights come on?'
    elif any(x in lowered for x in ('brake', 'braking')):
        reply = 'Does the noise happen only while braking? Is the pedal soft, and does the car pull to either side?'
    elif any(x in lowered for x in ('overheat', 'overheating', 'steam')):
        reply = 'How high does the temperature gauge rise? Is coolant leaking or is steam visible? Stop driving if it is overheating.'
    else:
        missing = _vehicle_info_gaps(full_context)
        if missing:
            reply = 'Thanks, I have the symptom details. To tailor the assessment, please share ' + ', '.join(missing) + '.'
        else:
            reply = 'Thanks, I have the vehicle details and warning-light information. You can generate a preliminary assessment now, or tell me when the symptom happens and whether anything changes it.'
    conversation.messages.create(role='assistant', content=reply)
    return {'reply': reply, 'status': 'follow_up', 'diagnosis_ready': False}
