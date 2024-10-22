from django.contrib.auth.models import Permission, User  # Nhập mô hình Permission và User từ Django để sử dụng thông tin người dùng và quyền hạn.
from django.core.validators import MaxValueValidator, MinValueValidator  # Nhập các bộ xác thực để kiểm tra giá trị tối đa và tối thiểu.
from django.db import models  # Nhập mô-đun models từ Django để tạo các mô hình cơ sở dữ liệu.

class Movie(models.Model):  # Định nghĩa mô hình Movie đại diện cho bảng phim.
    title = models.CharField(max_length=200)  # Trường để lưu tiêu đề phim, tối đa 200 ký tự.
    genre = models.CharField(max_length=100)  # Trường để lưu thể loại phim, tối đa 100 ký tự.
    movie_logo = models.FileField()  # Trường để lưu ảnh đại diện cho phim.

    def __str__(self):  # Phương thức trả về chuỗi mô tả cho đối tượng Movie.
        return self.title  # Trả về tiêu đề của phim khi in đối tượng.

class Myrating(models.Model):  # Định nghĩa mô hình Myrating đại diện cho bảng đánh giá phim.
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Trường liên kết đến mô hình User, cho biết ai đã đánh giá phim.
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)  # Trường liên kết đến mô hình Movie, chỉ định phim được đánh giá.
    rating = models.IntegerField(default=1, validators=[MaxValueValidator(5), MinValueValidator(0)])  # Trường để lưu đánh giá, mặc định là 1, với giá trị hợp lệ từ 0 đến 5.
