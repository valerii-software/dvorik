from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0002_message_image_alter_message_text'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Drop the unique pair so we can keep user_a/user_b around during migration.
        migrations.AlterUniqueTogether(name='dialog', unique_together=set()),
        # Add the new fields. user_a/user_b stay for now; data migration uses them.
        migrations.AddField(
            model_name='dialog',
            name='participants',
            field=models.ManyToManyField(related_name='chats', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dialog',
            name='name',
            field=models.CharField(blank=True, max_length=120, verbose_name='название'),
        ),
        migrations.AddField(
            model_name='dialog',
            name='created_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='created_chats',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name='dialog',
            options={'ordering': ['-last_message_at', '-id']},
        ),
    ]
