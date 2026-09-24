from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from .models import Conversation

class MechanicApiTests(APITestCase):
    def test_off_topic_is_rejected_without_ai(self):
        response = self.client.post('/api/chat/', {'message': 'Write a Python calculator.'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'off_topic')
        self.assertFalse(response.data['diagnosis_ready'])

    def test_chat_follow_up_and_history(self):
        first = self.client.post('/api/chat/', {'message': "My car won't start"}, format='json')
        self.assertEqual(first.status_code, 200)
        self.assertIn('crank', first.data['reply'].lower())
        conversation_id = first.data['conversation_id']
        second = self.client.post('/api/chat/', {'conversation_id': conversation_id, 'message': 'It only clicks and the lights are dim.'}, format='json')
        self.assertEqual(second.status_code, 200)
        history = self.client.get(f'/api/conversations/{conversation_id}/')
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.data['messages']), 4)

    def test_vehicle_details_provided_in_one_message_are_not_requested_again(self):
        first = self.client.post('/api/chat/', {'message': 'My Honda Civic has a starting problem.'}, format='json')
        conversation_id = first.data['conversation_id']
        response = self.client.post('/api/chat/', {
            'conversation_id': conversation_id,
            'message': 'Vehicle year - 2018, Make - Honda, Model - Civic. No warning lights are on.',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('share the vehicle year, make, model', response.data['reply'].lower())
        self.assertIn('generate a preliminary assessment', response.data['reply'].lower())

    def test_upload_rejects_unsupported_type(self):
        file = SimpleUploadedFile('notes.txt', b'not media', content_type='text/plain')
        response = self.client.post('/api/upload/', {'file': file}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['code'], 'INVALID_FILE_TYPE')

    def test_diagnosis_and_booking_flow(self):
        first = self.client.post('/api/chat/', {'message': "My car won't start and makes a clicking noise."}, format='json')
        conversation_id = first.data['conversation_id']
        self.client.post('/api/chat/', {'conversation_id': conversation_id, 'message': 'The dashboard lights are dim and it does not crank.'}, format='json')
        diagnosis = self.client.post('/api/diagnosis/', {'conversation_id': conversation_id}, format='json')
        self.assertEqual(diagnosis.status_code, 200)
        payload = {'conversation_id': conversation_id, 'diagnosis_id': diagnosis.data['diagnosis_id'], 'customer_name': 'Test Driver', 'phone': '+919876543210', 'email': 'driver@example.com', 'vehicle_make': 'Honda', 'vehicle_model': 'City', 'vehicle_year': 2021, 'problem_summary': diagnosis.data['probable_issue'], 'preferred_date': str(date.today() + timedelta(days=1)), 'preferred_time': '10:00'}
        booking = self.client.post('/api/booking/', payload, format='json')
        self.assertEqual(booking.status_code, 201)
        self.assertEqual(self.client.get(f"/api/booking/{booking.data['id']}/").status_code, 200)
        duplicate = self.client.post('/api/booking/', payload, format='json')
        self.assertEqual(duplicate.status_code, 409)
