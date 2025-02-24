from django.contrib import admin
from .models import Shift, Attendance, ShiftAssignment

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'duration_hours')
    search_fields = ('name',)
    ordering = ('start_time',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out', 'work_hours', 'overtime_hours')
    list_filter = ('date', 'employee')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'

@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift', 'date')
    list_filter = ('date', 'shift')
    search_fields = ('employee__first_name', 'employee__last_name', 'shift__name')
    date_hierarchy = 'date'
