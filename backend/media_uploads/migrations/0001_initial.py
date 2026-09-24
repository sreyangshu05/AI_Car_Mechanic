import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [('conversations','0001_initial')]
    operations = [migrations.CreateModel(name='MediaFile', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('file', models.FileField(upload_to='car-media/%Y/%m/')), ('file_type', models.CharField(max_length=10)), ('file_size', models.PositiveBigIntegerField()), ('created_at', models.DateTimeField(auto_now_add=True)), ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_files', to='conversations.conversation')), ('message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='media_files', to='conversations.message'))])]
