from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Attendance, Employee
from .forms import AttendanceForm, AttendanceQuickForm
import timedelta


# <----------------------------------------------  ------------------------------------------------->

@login_required
def attendance_list(request):
    attendances = Attendance.objects.select_related('employee').all()
    return render(request, 'attendances/attendance/list.html', {
        'attendances': attendances
    })

@login_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, 'Attendance record created successfully.')
            return redirect('attendance_detail', pk=attendance.pk)
    else:
        form = AttendanceForm()
    
    return render(request, 'attendances/attendance/form.html', {
        'form': form,
        'title': 'Create Attendance Record'
    })

@login_required
def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, 'Attendance record updated successfully.')
            return redirect('attendance_detail', pk=attendance.pk)
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'attendances/attendance/form.html', {
        'form': form,
        'title': 'Update Attendance Record'
    })

@login_required
def quick_attendance(request):
    if request.method == 'POST':
        form = AttendanceQuickForm(request.POST)
        if form.is_valid():
            employee = get_object_or_404(Employee, id=form.cleaned_data['employee_id'])
            action_type = form.cleaned_data['action_type']
            current_time = timezone.localtime().time()
            current_date = timezone.localtime().date()

            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=current_date,
                defaults={
                    'time_in': current_time if action_type == 'time_in' else None,
                    'time_out': current_time if action_type == 'time_out' else None,
                }
            )

            if not created:
                if action_type == 'time_in' and not attendance.time_in:
                    attendance.time_in = current_time
                elif action_type == 'time_out' and not attendance.time_out:
                    attendance.time_out = current_time
                attendance.save()

            messages.success(request, f'Successfully recorded {action_type} for {employee.full_name}')
            return redirect('attendance:attendance_list')

    return redirect('attendance:attendance_list')



# <---------------------------------------------- Quản lý ca làm việc ------------------------------------------------->



# <---------------------------------------------- Quản lý nghỉ phép ------------------------------------------------->
