# Generated by Django 5.1.6 on 2025-02-21 11:36

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '0003_laborcontract'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Shift Name')),
                ('start_time', models.TimeField(verbose_name='Start Time')),
                ('end_time', models.TimeField(verbose_name='End Time')),
            ],
            options={
                'verbose_name': 'Work Shift',
                'verbose_name_plural': 'Work Shifts',
                'db_table': 'Shift',
                'ordering': ['start_time'],
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Work Date')),
                ('time_in', models.TimeField(blank=True, null=True, verbose_name='Time In')),
                ('time_out', models.TimeField(blank=True, null=True, verbose_name='Time Out')),
                ('overtime_hours', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Overtime Hours')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='employee.employee', verbose_name='Employee')),
            ],
            options={
                'verbose_name': 'Attendance Record',
                'verbose_name_plural': 'Attendance Records',
                'db_table': 'Attendance',
                'ordering': ['-date', 'time_in'],
                'unique_together': {('employee', 'date')},
            },
        ),
        migrations.CreateModel(
            name='ShiftAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Assignment Date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_assignments', to='employee.employee', verbose_name='Employee')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='attendance.shift', verbose_name='Shift')),
            ],
            options={
                'verbose_name': 'Shift Assignment',
                'verbose_name_plural': 'Shift Assignments',
                'db_table': 'ShiftAssignment',
                'ordering': ['-date', 'shift__start_time'],
                'unique_together': {('employee', 'shift', 'date')},
            },
        ),
    ]
