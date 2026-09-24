import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [('conversations','0001_initial'), ('diagnosis','0001_initial')]
    operations = [migrations.CreateModel(name='Booking', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('customer_name', models.CharField(max_length=120)), ('phone', models.CharField(max_length=30)), ('email', models.EmailField(max_length=254)), ('vehicle_make', models.CharField(max_length=60)), ('vehicle_model', models.CharField(max_length=60)), ('vehicle_year', models.PositiveIntegerField()), ('problem_summary', models.TextField(max_length=2000)), ('preferred_date', models.DateField()), ('preferred_time', models.TimeField()), ('status', models.CharField(choices=[('pending','Pending'),('confirmed','Confirmed'),('cancelled','Cancelled')], default='confirmed', max_length=12)), ('created_at', models.DateTimeField(auto_now_add=True)), ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='conversations.conversation')), ('diagnosis', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='diagnosis.diagnosis'))])]
