from django.contrib import admin
from .models import Department, Employee, LaborContract



# Register your models here.

# <------------------------------------ Phòng ban ------------------------------------>
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_code', 'department_name', 'description')
    list_filter = ('department_name',)
    search_fields = ('department_code', 'department_name')
    ordering = ('department_code',)
    
    fieldsets = (
        ('Department Information', {
            'fields': ('department_code', 'department_name', 'description')
        }),
    )

# <------------------------------------ Nhân viên ------------------------------------>
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id', 
        'full_name', 
        'department', 
        'phone_number', 
        'hire_date',
        'age',
        'years_of_service'
    )
    
    list_filter = (
        'department', 
        'gender', 
        'hire_date'
    )
    
    search_fields = (
        'full_name', 
        'identity_card', 
        'email', 
        'phone_number'
    )
    
    ordering = ('-hire_date',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'full_name',
                'date_of_birth',
                'gender',
                'identity_card'
            )
        }),
        ('Contact Information', {
            'fields': (
                'email',
                'phone_number',
                'address'
            )
        }),
        ('Employment Information', {
            'fields': (
                'department',
                'hire_date'
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('employee_id', 'identity_card')
        return ()
    

# <------------------------------------ Hợp đồng lao động ------------------------------------>
@admin.register(LaborContract)
class LaborContractAdmin(admin.ModelAdmin):
    list_display = (
        'contract_id', 
        'employee', 
        'contract_type', 
        'start_date', 
        'end_date', 
        'base_salary',
        'is_active'
    )
    
    list_filter = ('contract_type', 'start_date', 'end_date')
    search_fields = ('employee__full_name', 'contract_id')
    ordering = ('-start_date',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'employee',
                'contract_type',
                'start_date',
                'end_date'
            )
        }),
        ('Salary Information', {
            'fields': ('base_salary',)
        }),
        ('Attachments', {
            'fields': ('contract_file',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('contract_id',)
        return ()