from django import forms
from .models import Attendance, ShiftAssignment, Shift
from employee.models import Employee
from django.core.exceptions import ValidationError


# <---------------------------------------------- Biểu mẫu chấm công ------------------------------------------------->
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'time_in', 'time_out', 'overtime_hours']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        time_in = cleaned_data.get('time_in')
        time_out = cleaned_data.get('time_out')
        
        if time_in and time_out and time_in >= time_out:
            raise forms.ValidationError("Time out must be after time in")
        
        return cleaned_data

class AttendanceQuickForm(forms.Form):
    employee_id = forms.CharField(widget=forms.HiddenInput())
    action_type = forms.ChoiceField(choices=[
        ('time_in', 'Time In'),
        ('time_out', 'Time Out')
    ])


# <---------------------------------------------- Biểu mẫu Quản lý ca làm việc ------------------------------------------------->


# <---------------------------------------------- Biểu mẫu Quản lý nghỉ phép ------------------------------------------------->