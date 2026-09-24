from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from conversations.models import Conversation
from core.constants import MAX_FILE_SIZE, ALL_ALLOWED_MIMES
from core.exceptions import error_response
from .models import MediaFile

class UploadView(APIView):
    def post(self, request):
        uploaded = request.FILES.get('file')
        conversation_id = request.data.get('conversation_id')
        if not uploaded:
            return error_response('FILE_REQUIRED', 'Attach an image, audio, or video file.')
        if uploaded.size > MAX_FILE_SIZE:
            return error_response('FILE_TOO_LARGE', 'Files must be 50MB or smaller.')
        mime = (uploaded.content_type or '').lower()
        if mime not in ALL_ALLOWED_MIMES:
            return error_response('INVALID_FILE_TYPE', 'Only supported image, audio, and video files are accepted.')
        if Path(uploaded.name).suffix.lower() not in {'.jpg','.jpeg','.png','.gif','.webp','.bmp','.mp3','.wav','.ogg','.aac','.flac','.webm','.mp4','.mov','.avi','.mkv'}:
            return error_response('INVALID_FILE_EXTENSION', 'The file extension is not supported.')
        if not conversation_id:
            conversation = Conversation.objects.create()
        else:
            try: conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist: return error_response('NOT_FOUND', 'Conversation not found.', 404)
        kind = mime.split('/')[0]
        media = MediaFile.objects.create(conversation=conversation, file=uploaded, file_type=kind, file_size=uploaded.size)
        return Response({'media_id': media.id, 'conversation_id': str(conversation.id), 'file_type': kind, 'url': request.build_absolute_uri(media.file.url), 'status': 'uploaded'}, status=status.HTTP_201_CREATED)
