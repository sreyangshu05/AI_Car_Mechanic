import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [('conversations','0001_initial')]
    operations = [migrations.CreateModel(name='Diagnosis', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('summary', models.TextField()), ('probable_issue', models.CharField(max_length=255)), ('severity', models.CharField(choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')], max_length=10)), ('recommended_action', models.TextField()), ('confidence', models.DecimalField(decimal_places=3, max_digits=4)), ('created_at', models.DateTimeField(auto_now_add=True)), ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diagnoses', to='conversations.conversation'))])]
