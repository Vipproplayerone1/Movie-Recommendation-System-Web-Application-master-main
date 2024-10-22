from django.contrib.auth.models import User  # Nhập mô hình User từ Django để sử dụng thông tin người dùng.
from django import forms  # Nhập mô-đun forms từ Django để tạo các biểu mẫu.

class UserForm(forms.ModelForm):  # Định nghĩa lớp UserForm kế thừa từ forms.ModelForm.
    password = forms.CharField(widget=forms.PasswordInput)  # Tạo trường password với widget là PasswordInput để ẩn mật khẩu.

    class Meta:  # Lớp bên trong Meta dùng để cấu hình mô hình và trường.
        model = User  # Chỉ định mô hình User sẽ được sử dụng.
        fields = ['username', 'email', 'password']  # Xác định các trường cần có trong biểu mẫu.
