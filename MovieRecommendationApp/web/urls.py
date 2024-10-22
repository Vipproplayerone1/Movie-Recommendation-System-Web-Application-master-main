from django.urls import path  # Nhập mô-đun path từ Django để định nghĩa các đường dẫn URL.

from . import views  # Nhập các hàm xử lý (view functions) từ module views trong cùng thư mục.

urlpatterns = [  # Định nghĩa danh sách các URL và các hàm xử lý tương ứng.
    path('', views.index, name='index'),  # Đường dẫn gốc sẽ gọi hàm index từ views.
    path('<int:movie_id>/', views.detail, name='detail'),  # Đường dẫn cho chi tiết phim, sử dụng movie_id để xác định phim cụ thể.
    path('signup/', views.signUp, name='signup'),  # Đường dẫn cho trang đăng ký người dùng, gọi hàm signUp.
    path('login/', views.Login, name='login'),  # Đường dẫn cho trang đăng nhập, gọi hàm Login.
    path('logout/', views.Logout, name='logout'),  # Đường dẫn cho chức năng đăng xuất, gọi hàm Logout.
    path('recommend/', views.recommend, name='recommend')  # Đường dẫn cho trang gợi ý phim, gọi hàm recommend.
]
