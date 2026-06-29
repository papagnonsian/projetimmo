from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annonces', '0007_favori'),
    ]

    operations = [
        migrations.AddField(
            model_name='demande',
            name='reponse_agent',
            field=models.TextField(blank=True, null=True, verbose_name="Réponse de l'agent"),
        ),
    ]
