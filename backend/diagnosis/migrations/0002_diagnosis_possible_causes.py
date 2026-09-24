from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [('diagnosis','0001_initial')]
    operations = [migrations.AddField(model_name='diagnosis', name='possible_causes', field=models.JSONField(default=list))]
