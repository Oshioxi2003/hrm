# Create your views here.
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from .models import Department, Employee, LaborContract
from .forms import DepartmentForm, EmployeeForm, LaborContractForm

from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied



import xlsxwriter
from io import BytesIO
from datetime import datetime,timedelta
from django.utils import timezone

# <--------------------------------------- Phân quyền ---------------------------------------->
class BasePermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'user_app:login'
    
    def get_required_roles(self):
        """Override trong các class con để xác định role được phép"""
        return ['admin', 'hr']
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.user_type in self.get_required_roles()
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            print("Please login to access this page.")
            return redirect('user_app:login')
        else:
            print(f"Access denied. User type: {self.request.user.user_type}")
            return redirect('employee:notification')

# Role-specific Mixins
class AdminOnlyMixin(BasePermissionMixin):
    """Chỉ Admin mới có quyền truy cập"""
    def get_required_roles(self):
        return ['admin']

class AdminHRMixin(BasePermissionMixin):
    """Admin và HR có quyền truy cập"""
    def get_required_roles(self):
        return ['admin', 'hr']

class ManagementMixin(BasePermissionMixin):
    """Admin, HR và Manager có quyền truy cập"""
    def get_required_roles(self):
        return ['admin', 'hr', 'manager']
# <--------------------------------------- Phòng ban ---------------------------------------->
# Hiện thị list phòng ban
class DepartmentListView(ManagementMixin, ListView):
    model = Department
    template_name = 'employee/department/list.html'
    context_object_name = 'departments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Department.objects.all().order_by('department_code')
        print(f"User {self.request.user.username} accessed department list")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Department List',
            'user_type': self.request.user.user_type,
            'can_create': self.request.user.user_type in ['admin', 'hr'],
            'can_edit': self.request.user.user_type in ['admin', 'hr'],
            'can_delete': self.request.user.user_type == 'admin'
        })
        return context

# Thêm chức năng thêm phòng bann
class DepartmentCreateView(AdminHRMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'employee/department/create.html'
    success_url = reverse_lazy('employee:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Department'
        return context

    def form_valid(self, form):
        department = form.save()
        print(f"Department {department.department_name} created by {self.request.user.username}")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error creating department. Please check the form.')
        return super().form_invalid(form)


# Thêm chức năng update phòng ban
class DepartmentUpdateView(AdminHRMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'employee/department/update.html'
    success_url = reverse_lazy('employee:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Department'
        return context

    def form_valid(self, form):
        department = form.save()
        print(f"Department {department.department_name} updated by {self.request.user.username}")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating department. Please check the form.')
        return super().form_invalid(form)

# Thêm chức năng xoá phòng ba
class DepartmentDeleteView(AdminOnlyMixin, DeleteView):
    model = Department
    template_name = 'employee/department/delete.html'
    success_url = reverse_lazy('employee:department_list')
    context_object_name = 'department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Department'
        return context

    def delete(self, request, *args, **kwargs):
        department = self.get_object()
        try:
            if department.employees.exists():
                print(f"Cannot delete department {department.department_name} - has active employees")
                return redirect('employee:department_list')
            
            print(f"Department {department.department_name} deleted by {request.user.username}")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            print(f"Error deleting department: {str(e)}")
            return redirect('employee:department_list')
        



# <--------------------------------------- Nhân viên ---------------------------------------->

class EmployeeListView(ManagementMixin, ListView):
    """Display employee list"""
    model = Employee
    template_name = 'employee/employees/list.html'
    context_object_name = 'employees'
    paginate_by = 10

    def get_queryset(self):
        # Kiểm tra user type
        if self.request.user.user_type == 'employee':
            # Nếu là employee, chỉ hiển thị thông tin của họ
            queryset = Employee.objects.filter(id=self.request.user.id).select_related('department')
        else:
            # Nếu là admin hoặc HR, hiển thị tất cả
            queryset = Employee.objects.all().select_related('department')
            
            # Filter by department if specified
            department_id = self.request.GET.get('department')
            if department_id:
                queryset = queryset.filter(department_id=department_id)

            # Search by name
            search_query = self.request.GET.get('search')
            if search_query:
                queryset = queryset.filter(full_name__icontains=search_query)

        return queryset.order_by('-hire_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_employee = self.request.user.user_type == 'employee'
        
        context.update({
            'title': 'My Information' if is_employee else 'Employee List',
            'departments': Department.objects.all() if not is_employee else None,
            'selected_department': self.request.GET.get('department') if not is_employee else None,
            'search_query': self.request.GET.get('search', '') if not is_employee else None,
            'can_create': self.request.user.user_type in ['admin', 'hr'],
            'can_edit': self.request.user.user_type in ['admin', 'hr'],
            'can_delete': self.request.user.user_type == 'admin',
            'is_employee': is_employee
        })
        return context


# Chức năng thêm nhân viên
class EmployeeCreateView(AdminHRMixin, CreateView):
    """Add new employee"""
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee/employees/create.html'
    success_url = reverse_lazy('employee:employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Employee'
        context['departments'] = Department.objects.all()
        return context

    def form_valid(self, form):
        try:
            employee = form.save(commit=False)
            # Add additional processing if needed
            employee.save()
            print(f"Employee {employee.full_name} created successfully by {self.request.user.username}")
            return super().form_valid(form)
        except Exception as e:
            print(f"Error creating employee: {str(e)}")
            return self.form_invalid(form)

class EmployeeUpdateView(AdminHRMixin, UpdateView):
    """Update employee information"""
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee/employees/create.html'
    success_url = reverse_lazy('employee:employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Update Employee Information',
            'departments': Department.objects.all(),
            'employee': self.object
        })
        return context

    def form_valid(self, form):
        try:
            employee = form.save()
            print(f"Employee {employee.full_name} updated by {self.request.user.username}")
            return super().form_valid(form)
        except Exception as e:
            print(f"Error updating employee: {str(e)}")
            return self.form_invalid(form)

class EmployeeDeleteView(AdminHRMixin, DeleteView):
    """Delete employee"""
    model = Employee
    template_name = 'employee/employees/delete.html'
    success_url = reverse_lazy('employee:employee_list')
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Employee'
        return context

    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        try:
            print(f"Employee {employee.full_name} deleted by {request.user.username}")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            print(f"Error deleting employee: {str(e)}")
            return redirect('employee:employee_list')

class EmployeeDetailView(ManagementMixin, DetailView):
    """View employee details"""
    model = Employee
    template_name = 'employee/employees/detail.html'
    context_object_name = 'employee'

    def get_object(self):
        if self.request.user.user_type == 'employee':
            # Nếu là employee, chỉ cho phép xem thông tin của chính họ
            return get_object_or_404(Employee, id=self.request.user.id)
        return super().get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.object
        is_employee = self.request.user.user_type == 'employee'

        context.update({
            'title': 'My Information' if is_employee else f'Employee Information: {employee.full_name}',
            'can_edit': self.request.user.user_type in ['admin', 'hr'],
            'can_delete': self.request.user.user_type == 'admin',
            'is_employee': is_employee
        })
        return context

def employee_export(request):
    """Export employee list to Excel"""
    if request.user.user_type == 'employee':
        return redirect('employee:notification')  # Không cho phép employee xuất file
    
    if request.user.user_type not in ['admin', 'hr']:
        return redirect('employee:notification')

    # Create Excel file
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Employees')

    # Add headers
    headers = [
        'Employee ID', 'Full Name', 'Date of Birth', 'Gender', 
        'ID Card', 'Email', 'Phone Number', 'Address',
        'Department', 'Hire Date'
    ]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Add data - Lấy tất cả nhân viên nếu là admin/hr
    employees = Employee.objects.all().select_related('department')
    for row, employee in enumerate(employees, 1):
        worksheet.write(row, 0, employee.employee_id)
        worksheet.write(row, 1, employee.full_name)
        worksheet.write(row, 2, employee.date_of_birth.strftime('%d/%m/%Y') if employee.date_of_birth else '')
        worksheet.write(row, 3, employee.get_gender_display())
        worksheet.write(row, 4, employee.identity_card)
        worksheet.write(row, 5, employee.email)
        worksheet.write(row, 6, employee.phone_number)
        worksheet.write(row, 7, employee.address)
        worksheet.write(row, 8, employee.department.department_name if employee.department else '')
        worksheet.write(row, 9, employee.hire_date.strftime('%d/%m/%Y') if employee.hire_date else '')

    workbook.close()
    output.seek(0)

    # Create response
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=employees_{datetime.now().strftime("%Y%m%d")}.xlsx'
    
    print(f"Employee list exported by {request.user.username}")
    return response



# <------------------------------------ Hợp đồng lao động ------------------------------------>
class LaborContractListView(AdminHRMixin, ListView):
    model = LaborContract
    template_name = 'employee/contracts/list.html'
    context_object_name = 'contracts'
    paginate_by = 10

    def get_queryset(self):
        queryset = LaborContract.objects.select_related('employee')
        
        # Filter by employee if specified
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by contract type
        contract_type = self.request.GET.get('type')
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)

        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = [c for c in queryset if c.is_active]
        elif status == 'expired':
            queryset = [c for c in queryset if not c.is_active]

        return queryset

class LaborContractCreateView(AdminHRMixin, CreateView):
    model = LaborContract
    form_class = LaborContractForm
    template_name = 'employee/contracts/form.html'
    success_url = reverse_lazy('employee:contract_list')

class LaborContractUpdateView(AdminHRMixin, UpdateView):
    model = LaborContract
    form_class = LaborContractForm
    template_name = 'employee/contracts/form.html'
    success_url = reverse_lazy('employee:contract_list')

class LaborContractDetailView(AdminHRMixin, DetailView):
    model = LaborContract
    template_name = 'employee/contracts/detail.html'
    context_object_name = 'contract'

class LaborContractDeleteView(AdminHRMixin, DeleteView):
    model = LaborContract
    template_name = 'employee/contracts/delete.html'
    success_url = reverse_lazy('employee:contract_list')

class ContractPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Advanced permission mixin for contract management
    Handles different permission levels for different user types
    """
    login_url = reverse_lazy('login')
    permission_denied_message = "Access denied due to insufficient permissions."
    
    # Define permission levels
    PERMISSION_LEVELS = {
        'admin': ['view', 'add', 'change', 'delete'],
        'hr': ['view', 'add', 'change'],
        'manager': ['view'],
        'employee': ['view_own']
    }

    def get_required_permission(self):
        """
        Determine required permission based on view type
        """
        if isinstance(self, CreateView):
            return 'add'
        elif isinstance(self, UpdateView):
            return 'change'
        elif isinstance(self, DeleteView):
            return 'delete'
        return 'view'

    def has_permission(self, user, permission):
        """
        Check if user has specific permission
        """
        if not user.is_authenticated:
            return False
            
        user_permissions = self.PERMISSION_LEVELS.get(user.user_type, [])
        return permission in user_permissions

    def test_func(self):
        """
        Test if the user has required permissions
        """
        user = self.request.user
        required_permission = self.get_required_permission()

        # Special handling for viewing own contracts
        if required_permission == 'view' and user.user_type == 'employee':
            if hasattr(self, 'get_object'):
                obj = self.get_object()
                return obj.employee.user == user
            return False

        return self.has_permission(user, required_permission)

    def handle_no_permission(self):
        """
        Handle permission denied cases with appropriate messages and redirects
        """
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Please login to access this page.")
            return super().handle_no_permission()

        messages.error(self.request, self.permission_denied_message)
        
        # Redirect based on user type
        if self.request.user.user_type == 'employee':
            return redirect('employee_dashboard')
        return redirect('dashboard')

    def dispatch(self, request, *args, **kwargs):
        """
        Enhanced dispatch method with logging and additional checks
        """
        try:
            # Log access attempt
            user_type = request.user.user_type if request.user.is_authenticated else 'anonymous'
            action = self.get_required_permission()
            print(f"Access attempt: {user_type} trying to {action} contract")

            # Additional security checks can be added here
            if request.user.is_authenticated and request.user.is_active:
                return super().dispatch(request, *args, **kwargs)
            
            raise PermissionDenied("User account is inactive.")

        except PermissionDenied as e:
            messages.error(request, str(e))
            return self.handle_no_permission()
        except Exception as e:
            messages.error(request, "An error occurred while processing your request.")
            print(f"Error in contract access: {str(e)}")
            return redirect('error_page')
        

# Views hợp đồng sắp hết hạn
class ExpiringContractsView(ContractPermissionMixin, ListView):
    model = LaborContract
    template_name = 'employee/contracts/expiring_contracts.html'
    context_object_name = 'contracts'
    paginate_by = 10

    def get_queryset(self):
        # Get current date
        today = timezone.now().date()
        
        # Calculate dates for filtering
        two_months_later = today + timedelta(days=60)  # 2 months
        
        # Filter contracts
        return LaborContract.objects.select_related('employee').filter(
            end_date__gt=today,
            end_date__lte=two_months_later
        ).order_by('end_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date
        today = timezone.now().date()
        
        # Calculate different time periods
        one_month_later = today + timedelta(days=30)
        two_months_later = today + timedelta(days=60)
        
        # Get counts for different periods
        context.update({
            'title': 'Expiring Contracts',
            'total_expiring': self.get_queryset().count(),
            'expire_this_month': LaborContract.objects.filter(
                end_date__gt=today,
                end_date__lte=one_month_later
            ).count(),
            'expire_next_month': LaborContract.objects.filter(
                end_date__gt=one_month_later,
                end_date__lte=two_months_later
            ).count(),
        })
        return context








# 
class NotificationView(LoginRequiredMixin, ListView):
    template_name = 'users/notification.html'
    model = Department
    context_object_name = 'departments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'title': 'Access Denied',
            'user_type': user.user_type,
            'username': user.get_full_name() or user.username,
            'current_role': user.get_user_type_display(),
            'required_roles': self.get_required_roles_display()
        })
        return context

    def get_required_roles_display(self):
        return {
            'admin': 'Administrator',
            'hr': 'HR Manager',
            'manager': 'Department Manager'
        }