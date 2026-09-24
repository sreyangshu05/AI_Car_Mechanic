import uuid
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name='Conversation', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('status', models.CharField(choices=[('active','Active'),('diagnosed','Diagnosed'),('booked','Booked')], db_index=True, default='active', max_length=20)), ('vehicle_info', models.JSONField(blank=True, null=True))]), migrations.CreateModel(name='Message', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('role', models.CharField(choices=[('user','User'),('assistant','Assistant'),('system','System')], max_length=10)), ('content', models.TextField()), ('message_type', models.CharField(choices=[('text','Text'),('image','Image'),('audio','Audio'),('video','Video')], default='text', max_length=10)), ('created_at', models.DateTimeField(auto_now_add=True)), ('conversation', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='messages', to='conversations.conversation'))])]
