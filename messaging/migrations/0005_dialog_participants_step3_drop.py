from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_dialog_participants_step2_data'),
    ]

    operations = [
        migrations.RemoveField(model_name='dialog', name='user_a'),
        migrations.RemoveField(model_name='dialog', name='user_b'),
    ]
