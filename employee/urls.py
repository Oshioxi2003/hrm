from django.urls import path
from . import views
from .views import DepartmentListView, DepartmentCreateView

app_name = 'employee'

urlpatterns = [
    # Url phòng ban
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('department/create/', DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    # Url Nhân viên
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('employees/export/', views.employee_export, name='employee_export'),

    # Url hợp đồng lao động
    path('contracts/', views.LaborContractListView.as_view(), name='contract_list'),
    path('contracts/create/', views.LaborContractCreateView.as_view(), name='contract_create'),
    path('contracts/<int:pk>/', views.LaborContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<int:pk>/update/', views.LaborContractUpdateView.as_view(), name='contract_update'),
    path('contracts/<int:pk>/delete/', views.LaborContractDeleteView.as_view(), name='contract_delete'),
    path('contracts/expiring/', views.ExpiringContractsView.as_view(), name='expiring_contracts'),

    
    #Url phân quyền 
    path('notification/', views.NotificationView.as_view(), name='notification'),
]