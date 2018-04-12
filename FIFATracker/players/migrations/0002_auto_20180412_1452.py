# Generated by Django 2.0 on 2018-04-12 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datausersplayers',
            name='commonnameid',
        ),
        migrations.RemoveField(
            model_name='datausersplayers',
            name='firstnameid',
        ),
        migrations.RemoveField(
            model_name='datausersplayers',
            name='lastnameid',
        ),
        migrations.RemoveField(
            model_name='datausersplayers',
            name='playerjerseynameid',
        ),
        migrations.RemoveField(
            model_name='datausersplayers17',
            name='commonnameid',
        ),
        migrations.RemoveField(
            model_name='datausersplayers17',
            name='firstnameid',
        ),
        migrations.RemoveField(
            model_name='datausersplayers17',
            name='lastnameid',
        ),
        migrations.RemoveField(
            model_name='datausersplayers17',
            name='playerjerseynameid',
        ),
        migrations.AddField(
            model_name='datausersplayers',
            name='commonname',
            field=models.ForeignKey(db_column='commonnameid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commonname', to='players.DataPlayernames'),
        ),
        migrations.AddField(
            model_name='datausersplayers',
            name='firstname',
            field=models.ForeignKey(db_column='firstnameid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='firstname', to='players.DataPlayernames'),
        ),
        migrations.AddField(
            model_name='datausersplayers',
            name='lastname',
            field=models.ForeignKey(db_column='lastnameid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lastname', to='players.DataPlayernames'),
        ),
        migrations.AddField(
            model_name='datausersplayers',
            name='playerjerseyname',
            field=models.ForeignKey(db_column='playerjerseynameid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playerjerseyname', to='players.DataPlayernames'),
        ),
        migrations.AddField(
            model_name='datausersplayers17',
            name='commonname',
            field=models.ForeignKey(db_column='commonnameid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commonname', to='players.DataPlayernames17'),
        ),
        migrations.AddField(
            model_name='datausersplayers17',
            name='firstname',
            field=models.ForeignKey(db_column='firstnameid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='firstname', to='players.DataPlayernames17'),
        ),
        migrations.AddField(
            model_name='datausersplayers17',
            name='lastname',
            field=models.ForeignKey(db_column='lastnameid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lastname', to='players.DataPlayernames17'),
        ),
        migrations.AddField(
            model_name='datausersplayers17',
            name='playerjerseyname',
            field=models.ForeignKey(db_column='playerjerseynameid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playerjerseyname', to='players.DataPlayernames17'),
        ),
    ]
