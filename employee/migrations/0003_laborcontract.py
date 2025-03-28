# Generated by Django 5.1.6 on 2025-02-20 03:14

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0002_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaborContract',
            fields=[
                ('contract_id', models.AutoField(primary_key=True, serialize=False, verbose_name='Contract ID')),
                ('contract_type', models.CharField(choices=[('Probation', 'Probation'), ('Permanent', 'Permanent'), ('Temporary', 'Temporary')], max_length=20, verbose_name='Contract Type')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('base_salary', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Base Salary')),
                ('contract_file', models.FileField(blank=True, null=True, upload_to='contracts/', verbose_name='Attached File')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labor_contracts', to='employee.employee', verbose_name='Employee')),
            ],
            options={
                'verbose_name': 'Labor Contract',
                'verbose_name_plural': 'Labor Contracts',
                'db_table': 'LaborContract',
                'ordering': ['-start_date'],
            },
        ),
    ]
