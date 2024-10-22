from django.contrib.auth import authenticate, login, logout  # Nhập các hàm xác thực và quản lý phiên làm việc cho người dùng.
from django.shortcuts import render, get_object_or_404, redirect  # Nhập các hàm để xử lý yêu cầu và phản hồi.
from django.db.models import Q  # Nhập Q để tạo các truy vấn phức tạp.
from django.http import Http404  # Nhập Http404 để xử lý lỗi không tìm thấy trang.
from django.contrib import messages  # Nhập mô-đun messages để hiển thị thông báo cho người dùng.
from .models import Movie, Myrating  # Nhập các mô hình Movie và Myrating từ ứng dụng web.
from .forms import UserForm  # Nhập form người dùng.
import numpy as np  # Nhập thư viện NumPy để làm việc với mảng và tính toán số học.
import pandas as pd  # Nhập thư viện pandas để làm việc với dữ liệu dạng bảng.
from sklearn.metrics.pairwise import cosine_similarity  # Nhập hàm tính độ tương đồng cosine từ scikit-learn.

def recommend(request):
    # Hàm gợi ý phim cho người dùng hiện tại dựa trên đánh giá của họ và những người dùng khác.
    if not request.user.is_authenticated:
        return redirect("login")  # Chuyển hướng đến trang đăng nhập nếu người dùng chưa đăng nhập.
    if not request.user.is_active:
        raise Http404()  # Ném lỗi 404 nếu người dùng không hoạt động.

    # Lấy dữ liệu đánh giá và loại bỏ trùng lặp
    df = pd.DataFrame(list(Myrating.objects.all().values()))  # Lấy tất cả đánh giá và chuyển đổi thành DataFrame.
    df = df.drop_duplicates(subset=['user_id', 'movie_id'])  # Loại bỏ các đánh giá trùng lặp.

    current_user_id = request.user.id  # Lấy ID của người dùng hiện tại.

    # Kiểm tra xem người dùng đã đánh giá phim nào chưa
    if df[df['user_id'] == current_user_id].empty:
        messages.error(request, "Bạn chưa đánh giá phim nào.")  # Hiển thị thông báo lỗi nếu người dùng chưa đánh giá.
        return redirect("index")  # Chuyển hướng về trang chính.

    # Pivot ma trận Y và tạo ánh xạ cho user_id và movie_id
    Y_df = df.pivot(index='movie_id', columns='user_id', values='rating').fillna(0)  # Tạo ma trận đánh giá.
    Y = Y_df.values  # Ma trận đánh giá (movies x users).
    R = (Y != 0).astype(int)  # Ma trận nhị phân (1: đã đánh giá, 0: chưa đánh giá).

    # Tạo dictionary ánh xạ user_id -> index
    user_id_to_index = {user_id: idx for idx, user_id in enumerate(Y_df.columns)}  # Tạo ánh xạ giữa user_id và chỉ số trong ma trận.

    # Kiểm tra nếu user_id hiện tại có trong ánh xạ
    if current_user_id not in user_id_to_index:
        messages.error(request, "Không tìm thấy người dùng.")  # Hiển thị thông báo lỗi nếu không tìm thấy người dùng.
        return redirect("index")

    current_user_index = user_id_to_index[current_user_id]  # Lấy chỉ số của người dùng hiện tại.

    # Chuẩn hóa và tính độ tương đồng người dùng
    Y_mean = np.mean(Y, axis=1, keepdims=True)  # Tính giá trị trung bình cho mỗi phim.
    Y_normalized = Y - Y_mean  # Chuẩn hóa ma trận đánh giá.
    user_similarity = cosine_similarity(Y_normalized.T)  # Tính độ tương đồng giữa các người dùng.

    # In ra ma trận tương đồng giữa các người dùng
    print("Ma trận tương đồng người dùng:\n", user_similarity)

    # Lấy danh sách người dùng tương tự
    similar_users = np.argsort(user_similarity[current_user_index])[::-1][1:5]  # Lấy 5 người dùng tương tự nhất.
    print(f"Người dùng hiện tại: {current_user_id}, Chỉ số trong ma trận: {current_user_index}")
    print(f"Những người dùng tương tự: {similar_users}")

    recommended_movies = set()  # Tạo tập hợp để lưu các phim gợi ý.
    user_seen_movies = np.where(R[:, current_user_index] == 1)[0]  # Lấy chỉ số phim đã xem bởi người dùng hiện tại.
    print(f"Phim đã xem bởi người dùng hiện tại: {user_seen_movies}")

    # Gợi ý phim từ những người dùng tương tự
    for user in similar_users:
        user_seen_movies_sim = np.where(R[:, user] == 1)[0]  # Lấy phim đã xem bởi người dùng tương tự.
        print(f"Phim đã xem bởi người dùng tương tự {user}: {user_seen_movies_sim}")

        for movie_id in user_seen_movies_sim:
            if movie_id not in user_seen_movies:
                recommended_movies.add(movie_id)  # Thêm phim vào danh sách gợi ý nếu người dùng chưa xem.

    # Kiểm tra nếu không có phim nào được gợi ý
    if not recommended_movies:
        messages.info(request, "Không có phim nào để gợi ý.")  # Hiển thị thông báo nếu không có phim gợi ý.
        return redirect("index")  # Chuyển hướng về trang chính.

    # Lấy thông tin phim từ cơ sở dữ liệu
    movie_list = Movie.objects.filter(id__in=recommended_movies)[:10]  # Lấy 10 phim gợi ý từ cơ sở dữ liệu.
    print(f"Phim được gợi ý: {recommended_movies}")

    return render(request, 'web/recommend.html', {'movie_list': movie_list})  # Render trang gợi ý với danh sách phim.

def index(request):
    # Hàm hiển thị trang chính với danh sách phim.
    movies = Movie.objects.all()  # Lấy tất cả phim từ cơ sở dữ liệu.
    query = request.GET.get('q')  # Lấy truy vấn tìm kiếm từ URL.
    if query:
        movies = Movie.objects.filter(Q(title__icontains=query)).distinct()  # Lọc phim theo tiêu đề nếu có truy vấn.
    return render(request, 'web/list.html', {'movies': movies})  # Render trang danh sách phim.

def detail(request, movie_id):
    # Hàm hiển thị chi tiết phim.
    if not request.user.is_authenticated:
        return redirect("login")  # Chuyển hướng đến trang đăng nhập nếu người dùng chưa đăng nhập.

    movies = get_object_or_404(Movie, id=movie_id)  # Lấy phim từ cơ sở dữ liệu hoặc trả về lỗi 404.
    if request.method == "POST":
        rate = request.POST['rating']  # Lấy đánh giá từ biểu mẫu.
        ratingObject = Myrating(user=request.user, movie=movies, rating=rate)  # Tạo đối tượng đánh giá mới.
        ratingObject.save()  # Lưu đánh giá vào cơ sở dữ liệu.
        messages.success(request, "Đánh giá của bạn đã được ghi nhận.")  # Hiển thị thông báo thành công.
        return redirect("index")  # Chuyển hướng về trang chính.

    return render(request, 'web/detail.html', {'movies': movies})  # Render trang chi tiết phim.

def signUp(request):
    # Hàm xử lý đăng ký người dùng.
    form = UserForm(request.POST or None)  # Khởi tạo biểu mẫu với dữ liệu POST (nếu có).
    if form.is_valid():  # Kiểm tra tính hợp lệ của biểu mẫu.
        user = form.save(commit=False)  # Tạo đối tượng người dùng mà chưa lưu vào cơ sở dữ liệu.
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)  # Mã hóa mật khẩu trước khi lưu.
        user.save()  # Lưu đối tượng người dùng vào cơ sở dữ liệu.
        user = authenticate(username=username, password=password)  # Xác thực người dùng vừa đăng ký.
        if user and user.is_active:
            login(request, user)  # Đăng nhập người dùng.
            return redirect("index")  # Chuyển hướng về trang chính.
    return render(request, 'web/signUp.html', {'form': form})  # Render trang đăng ký với biểu mẫu.

def Login(request):
    # Hàm xử lý đăng nhập người dùng.
    if request.method == "POST":
        username = request.POST['username']  # Lấy tên đăng nhập từ biểu mẫu.
        password = request.POST['password']  # Lấy mật khẩu từ biểu mẫu.
        user = authenticate(username=username, password=password)  # Xác thực thông tin đăng nhập.
        if user and user.is_active:
            login(request, user)  # Đăng nhập người dùng.
            return redirect("index")  # Chuyển hướng về trang chính.
        else:
            return render(request, 'web/login.html', {'error_message': 'Thông tin đăng nhập không chính xác.'})  # Hiển thị thông báo lỗi nếu đăng nhập thất bại.
    return render(request, 'web/login.html')  # Render trang đăng nhập.

def Logout(request):
    # Hàm xử lý đăng xuất người dùng.
    logout(request)  # Đăng xuất người dùng.
    return redirect("login")  # Chuyển hướng đến trang đăng nhập.
