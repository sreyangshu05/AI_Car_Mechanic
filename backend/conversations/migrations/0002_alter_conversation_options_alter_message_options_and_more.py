from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('conversations', '0001_initial')]
    operations = [
        migrations.AlterModelOptions(name='conversation', options={'ordering': ['-created_at']}),
        migrations.AlterModelOptions(name='message', options={'ordering': ['created_at']}),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['conversation', 'created_at'], name='conversatio_convers_4b968d_idx'),
        ),
    ]
