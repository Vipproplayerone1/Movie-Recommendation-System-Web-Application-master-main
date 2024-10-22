#!/usr/bin/env python  # Chỉ định interpreter Python để chạy script này.

import os  # Nhập mô-đun os để tương tác với hệ thống tệp.
import sys  # Nhập mô-đun sys để truy cập các biến và hàm Python của hệ thống.

if __name__ == "__main__":  # Kiểm tra xem script có được chạy trực tiếp không.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")  # Đặt biến môi trường cho cài đặt Django.

    try:
        from django.core.management import execute_from_command_line  # Nhập hàm để thực thi các lệnh quản lý Django.
    except ImportError as exc:  # Bắt lỗi ImportError nếu không thể nhập Django.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc  # Ném lỗi nếu Django không được cài đặt hoặc không có trong PYTHONPATH.

    execute_from_command_line(sys.argv)  # Thực thi lệnh quản lý Django với các đối số dòng lệnh.
