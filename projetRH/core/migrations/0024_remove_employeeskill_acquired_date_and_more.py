# Generated by Django 5.1.4 on 2025-01-17 14:06

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_remove_contract_created_at_remove_contract_document_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeeskill',
            name='acquired_date',
        ),
        migrations.AddField(
            model_name='employeeskill',
            name='acquisition_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='employeeskill',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_skills', to='core.employee'),
        ),
        migrations.AlterField(
            model_name='employeeskill',
            name='level',
            field=models.CharField(choices=[('Débutant', 'Débutant'), ('Intermédiaire', 'Intermédiaire'), ('Avancé', 'Avancé')], default='Débutant', max_length=50),
        ),
        migrations.AlterField(
            model_name='employeeskill',
            name='skill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skill_employees', to='core.skill'),
        ),
    ]
