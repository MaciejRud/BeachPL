# Generated by Django 5.0.9 on 2024-10-01 13:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_rename_points_user_total_points_user_gender_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='teams',
        ),
        migrations.CreateModel(
            name='PlayerTournamentResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_awarded', models.PositiveIntegerField()),
                ('position', models.PositiveIntegerField()),
                ('tournament_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_results', to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_results', to='core.team')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_results', to='core.tournament')),
            ],
        ),
        migrations.DeleteModel(
            name='TournamentResult',
        ),
    ]
