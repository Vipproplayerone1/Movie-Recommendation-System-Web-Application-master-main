from django.contrib import admin  # Nhập mô-đun admin từ Django để sử dụng giao diện quản trị.
from .models import Movie, Myrating  # Nhập các mô hình Movie và Myrating từ file models.py trong cùng thư mục.

# Đăng ký mô hình Movie với giao diện quản trị của Django.
admin.site.register(Movie)

# Đăng ký mô hình Myrating với giao diện quản trị của Django.
admin.site.register(Myrating)

# Ghi chú: Bạn có thể thêm nhiều mô hình khác để đăng ký tại đây nếu cần.
