from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from users.models import MyUser
from users.forms import UserCreateForm, UserUpdateForm, CustomerUpdateForm, CustomerProfileForm




# - Kế thừa LoginView của Django để xử lý đăng nhập người dùng
# - Sử dụng template tùy chỉnh 'users/login.html'
# - Hiển thị thông báo chào mừng khi đăng nhập thành công
# - Chuyển hướng đến trang chủ sau khi đăng nhập 

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_success_url(self):
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return reverse_lazy('user_app:home')



# - Xử lý chức năng đăng xuất người dùng
# - Hiển thị thông báo xác nhận đăng xuất
# - Chuyển hướng về trang đăng nhập sau khi đăng xuất
# - Xử lý cả yêu cầu GET và POST cho việc đăng xuất
class CustomLogoutView(LogoutView):
    template_name = 'users/logout.html'
    next_page = 'user_app:login'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Nếu request là POST hoặc GET, đều xử lý logout
            response = super().dispatch(request, *args, **kwargs)
            return response
        return redirect('user_app:login')


# - Kết hợp LoginRequiredMixin và UserPassesTestMixin
# - Đảm bảo người dùng đã được xác thực
# - Kiểm tra xem người dùng có phải là admin không
# - Chuyển hướng người dùng không có quyền về trang đăng nhập kèm thông báo lỗi

class MyMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'user_app:login'
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'admin'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Please login to access this page.")
            return redirect('user_app:login')
        else:
            
            return redirect('user_app:notification')

# Thêm view mới cho notification
class NotificationView(LoginRequiredMixin, ListView):
    template_name = 'users/notification.html'
    model = MyUser
    context_object_name = 'notifications'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Access Denied'
        return context


# - Yêu cầu đăng nhập để truy cập
# - Hiển thị bảng điều khiển với thống kê người dùng
# - Hiển thị số lượng admin và khách hàng
@login_required(login_url='user_app:login')
def home(request):
    """Dashboard hiển thị thống kê người dùng"""
    context = {
        'admin_count': MyUser.objects.filter(user_type='admin').count(),
        'hr_count': MyUser.objects.filter(user_type='hr').count(),
        'manager_count': MyUser.objects.filter(user_type='manager').count(),
        'employee_count': MyUser.objects.filter(user_type='employee').count(),
        'total_users': MyUser.objects.count(),
    }
    print(f"Dashboard statistics loaded: {context}")
    return render(request, 'users/home.html', context)




# - Hiển thị danh sách tất cả người dùng
# - Chỉ admin mới truy cập được (thông qua MyMixin)
# - Sắp xếp người dùng theo ngày tham gia
class UserListView(MyMixin, ListView):
    model = MyUser
    template_name = 'users/user/list.html'
    context_object_name = 'data'

    def get_queryset(self):
        return MyUser.objects.all().order_by('-date_joined')


# - Xử lý việc tạo người dùng mới
# - Chỉ admin mới truy cập được
# - Thiết lập mật khẩu người dùng an toàn
# - Hiển thị thông báo thành công sau khi tạo
class UserCreateView(MyMixin, CreateView):
    model = MyUser
    form_class = UserCreateForm
    template_name = 'users/user/create.html'
    success_url = reverse_lazy('user_app:list')

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        messages.success(self.request, f"{user.username} is created successfully!")
        return redirect(self.success_url)
    
    
# - Xử lý cập nhật thông tin người dùng
# - Chỉ admin mới truy cập được
# - Hiển thị thông báo thành công sau khi cập nhật
class UserUpdateView(MyMixin, UpdateView):
    model = MyUser
    form_class = UserUpdateForm
    template_name = 'users/user/update.html'
    success_url = reverse_lazy('user_app:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "User updated successfully!")
        return response


# - Xử lý xóa người dùng
# - Chỉ admin mới truy cập được
# - Hiển thị thông báo cảnh báo sau khi xóa
class UserDeleteView(MyMixin, DeleteView):
    model = MyUser
    template_name = 'users/user/delete.html'
    success_url = reverse_lazy('user_app:list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "User deleted successfully!")
        return super().delete(request, *args, **kwargs)


# - Xử lý cập nhật hồ sơ người dùng
# - Yêu cầu đăng nhập nhưng không cần quyền admin
# - Quản lý cả dữ liệu người dùng và ảnh đại diện
# - Xử lý hai biểu mẫu: CustomerUpdateForm và CustomerProfileForm
class UserProfile(LoginRequiredMixin, UpdateView):
    model = MyUser
    template_name = 'users/profile.html'
    login_url = 'user_app:login'

    def get(self, request, **kwargs):
        user = request.user
        data = MyUser.objects.get(id=user.id)
        c_form = CustomerUpdateForm(instance=user)
        p_form = CustomerProfileForm(instance=user.profile)

        context = {
            'data': data,
            'c_form': c_form,
            'p_form': p_form,
        }
        return render(request, 'users/profile.html', context)

    def post(self, request, *args, **kwargs):
        user = request.user
        c_form = CustomerUpdateForm(request.POST, instance=user)
        p_form = CustomerProfileForm(request.POST, request.FILES, instance=user.profile)
        
        if c_form.is_valid() and p_form.is_valid():
            c_form.save()
            p_form.save()
            print(f"Profile updated successfully!")
            return redirect('user_app:profile', pk=user.id)
        
        return render(request, 'users/profile.html', {
            'data': user,
            'c_form': c_form,
            'p_form': p_form,
        })
    


# - Xử lý đăng ký người dùng mới
# - Truy cập công khai (không cần đăng nhập)
# - Tạo tài khoản người dùng mới
# - Thiết lập mật khẩu an toàn
# - Chuyển hướng đến trang đăng nhập sau khi đăng ký thành công
class UserRegistrationView(CreateView):
    model = MyUser
    form_class = UserCreateForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('user_app:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        print(f"Registration successful. Please login.")
        return redirect(self.success_url)
    



class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset/password_reset.html'
    email_template_name = 'users/password_reset/password_reset_email.html'
    success_url = reverse_lazy('user_app:password_reset_done')
    subject_template_name = 'users/password_reset/password_reset_subject.txt'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset/password_reset_confirm.html'
    success_url = reverse_lazy('user_app:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset/password_reset_complete.html'