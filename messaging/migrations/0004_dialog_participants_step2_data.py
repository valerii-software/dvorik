from django.db import migrations


def copy_to_participants(apps, schema_editor):
    Dialog = apps.get_model('messaging', 'Dialog')
    for d in Dialog.objects.all():
        if d.user_a_id:
            d.participants.add(d.user_a_id)
        if d.user_b_id:
            d.participants.add(d.user_b_id)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0003_dialog_participants_step1'),
    ]

    operations = [
        migrations.RunPython(copy_to_participants, reverse_noop),
    ]
