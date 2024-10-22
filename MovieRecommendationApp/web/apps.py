from django.apps import AppConfig  # Nhập AppConfig từ Django để tạo cấu hình cho ứng dụng.

class WebConfig(AppConfig):  # Định nghĩa lớp WebConfig, kế thừa từ AppConfig.
    name = 'web'  # Thiết lập tên của ứng dụng là 'web'.
