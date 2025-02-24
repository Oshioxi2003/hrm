from django.urls import path
from . import views 

app_name = 'user_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'), 
    path('user/list/', views.UserListView.as_view(), name='list'),
    path('user/create/', views.UserCreateView.as_view(), name='create'),
    path('user/update/<int:pk>/', views.UserUpdateView.as_view(), name='update'),
    path('user/delete/<int:pk>/', views.UserDeleteView.as_view(), name='delete'),
    path('user/register/', views.UserRegistrationView.as_view(), name='register'),
    path('user/profile/<int:pk>/', views.UserProfile.as_view(), name='profile'),
    path('notification/', views.NotificationView.as_view(), name='notification'),

    # url quên mật khẩu
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
