from django.db import migrations, models


def move_votefact_variant(apps, schema_editor):
    VoteFact = apps.get_model('main', 'VoteFact')
    for vote_fact in VoteFact.objects.all():
        vote_fact.variants.add(vote_fact.variant)
        vote_fact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20210114_1912'),
    ]

    operations = [
        migrations.RunPython(move_votefact_variant),
        migrations.RemoveField(
            model_name='votefact',
            name='variant',
        ),
    ]
