from django import forms
from .models import Department, Employee, LaborContract



# <------------------------------- Phòng ban ----------------------------------->
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_code', 'department_name', 'description']
        widgets = {
            'department_code': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter department code'
                }
            ),
            'department_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter department name'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Enter department description'
                }
            ),
        }

    def clean_department_code(self):
        department_code = self.cleaned_data.get('department_code')
        if Department.objects.filter(department_code=department_code).exists():
            raise forms.ValidationError('Department code already exists')
        return department_code


# <------------------------------- Nhân viên ----------------------------------->
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        exclude = ['employee_id']
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'hire_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'address': forms.Textarea(
                attrs={'rows': 3}
            ),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone = phone.replace(' ', '')
            if not phone.startswith('+84') and not phone.startswith('0'):
                raise forms.ValidationError(
                    'Phone number must start with +84 or 0'
                )
        return phone

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('date_of_birth')
        hire_date = cleaned_data.get('hire_date')

        if date_of_birth and hire_date:
            if date_of_birth > hire_date:
                raise forms.ValidationError(
                    'Date of birth cannot be after hire date'
                )


# <------------------------------- Hợp đồng lao động ----------------------------------->
class LaborContractForm(forms.ModelForm):
    class Meta:
        model = LaborContract
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(
                attrs={
                    'type': 'date', 
                    'class': 'form-control',
                    'placeholder': 'Select start date'
                }
            ),
            'end_date': forms.DateInput(
                attrs={
                    'type': 'date', 
                    'class': 'form-control',
                    'placeholder': 'Select end date'
                }
            ),
            'base_salary': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '0.01',
                    'placeholder': 'Enter base salary'
                }
            ),
            'contract_type': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select contract type'
                }
            ),
            'employee': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select employee'
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        contract_type = cleaned_data.get('contract_type')

        if contract_type == 'Probation' and not end_date:
            raise forms.ValidationError(
                'Probation contract must have an end date'
            )

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                'End date must be after start date'
            )

        return cleaned_data
