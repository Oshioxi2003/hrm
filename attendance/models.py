from django.db import models
from employee.models import Employee  # Import Employee model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.utils import timezone
from datetime import datetime, time


class Shift(models.Model):
    """Model for work shifts"""
    
    name = models.CharField(
        max_length=50,
        verbose_name='Shift Name',
        unique=True
    )
    
    start_time = models.TimeField(
        verbose_name='Start Time'
    )
    
    end_time = models.TimeField(
        verbose_name='End Time'
    )

    class Meta:
        db_table = 'Shift'
        verbose_name = 'Work Shift'
        verbose_name_plural = 'Work Shifts'
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('End time must be after start time')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def duration_hours(self):
        """Calculate shift duration in hours"""
        if self.start_time and self.end_time:
            start = timezone.datetime.combine(timezone.now(), self.start_time)
            end = timezone.datetime.combine(timezone.now(), self.end_time)
            duration = end - start
            return duration.total_seconds() / 3600
        return 0

class Attendance(models.Model):
    """Model for attendance records"""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Employee'
    )
    
    date = models.DateField(
        verbose_name='Work Date',
        default=timezone.now
    )
    
    time_in = models.TimeField(
        verbose_name='Time In',
        null=True,
        blank=True
    )
    
    time_out = models.TimeField(
        verbose_name='Time Out',
        null=True,
        blank=True
    )
    
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Overtime Hours'
    )

    class Meta:
        db_table = 'Attendance'
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        ordering = ['-date', 'time_in']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    def clean(self):
        if self.time_in and self.time_out:
            if self.time_in >= self.time_out:
                raise ValidationError('Time out must be after time in')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def work_hours(self):
        """Calculate total work hours"""
        if self.time_in and self.time_out:
            start = timezone.datetime.combine(timezone.now(), self.time_in)
            end = timezone.datetime.combine(timezone.now(), self.time_out)
            duration = end - start
            return duration.total_seconds() / 3600
        return 0

class ShiftAssignment(models.Model):
    """Model for shift assignments"""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='shift_assignments',
        verbose_name='Employee'
    )
    
    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Shift'
    )
    
    date = models.DateField(
        verbose_name='Assignment Date',
        default=timezone.now
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'ShiftAssignment'
        verbose_name = 'Shift Assignment'
        verbose_name_plural = 'Shift Assignments'
        ordering = ['-date', 'shift__start_time']
        unique_together = ['employee', 'shift', 'date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.shift.name} ({self.date})"

    def clean(self):
        # Check if employee already has a shift assigned for this date
        existing = ShiftAssignment.objects.filter(
            employee=self.employee,
            date=self.date
        ).exclude(id=self.id)
        
        if existing.exists():
            raise ValidationError(
                f'Employee already has a shift assigned on {self.date}'
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
