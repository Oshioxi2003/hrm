from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # <----------------------------------------------  ------------------------------------------------->

    path('list/', views.attendance_list, name='attendance_list'),
    path('create/', views.attendance_create, name='attendance_create'),
    path('<int:pk>/update/', views.attendance_update, name='attendance_update'),
    path('quick-attendance/', views.quick_attendance, name='quick_attendance'),

    # <----------------------------------------------  ------------------------------------------------->



    # <----------------------------------------------  ------------------------------------------------->



]
