from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annonces', '0006_agence_premium_jusqu_au'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favori',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_ajout', models.DateTimeField(auto_now_add=True)),
                ('bien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoris', to='annonces.bien')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoris', to='annonces.client')),
            ],
            options={
                'verbose_name': 'Favori',
                'verbose_name_plural': 'Favoris',
                'ordering': ['-date_ajout'],
                'unique_together': {('client', 'bien')},
            },
        ),
    ]
