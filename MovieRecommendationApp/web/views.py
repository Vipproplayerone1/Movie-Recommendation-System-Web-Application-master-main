from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import Http404
from django.contrib import messages
from .models import Movie, Myrating
from .forms import UserForm
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def recommend(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404()

    # Lấy dữ liệu đánh giá và loại bỏ trùng lặp
    df = pd.DataFrame(list(Myrating.objects.all().values()))
    df = df.drop_duplicates(subset=['user_id', 'movie_id'])

    current_user_id = request.user.id

    # Kiểm tra xem người dùng đã đánh giá phim nào chưa
    if df[df['user_id'] == current_user_id].empty:
        messages.error(request, "Bạn chưa đánh giá phim nào.")
        return redirect("index")

    # Pivot ma trận Y và tạo ánh xạ cho user_id và movie_id
    Y_df = df.pivot(index='movie_id', columns='user_id', values='rating').fillna(0)
    Y = Y_df.values  # Ma trận đánh giá (movies x users)
    R = (Y != 0).astype(int)  # Ma trận nhị phân (1: đã đánh giá, 0: chưa đánh giá)

    # Tạo dictionary ánh xạ user_id -> index
    user_id_to_index = {user_id: idx for idx, user_id in enumerate(Y_df.columns)}

    # Kiểm tra nếu user_id hiện tại có trong ánh xạ
    if current_user_id not in user_id_to_index:
        messages.error(request, "Không tìm thấy người dùng.")
        return redirect("index")

    current_user_index = user_id_to_index[current_user_id]

    # Chuẩn hóa và tính độ tương đồng người dùng
    Y_mean = np.mean(Y, axis=1, keepdims=True)  # Trung bình mỗi bộ phim
    Y_normalized = Y - Y_mean  # Chuẩn hóa ma trận đánh giá
    user_similarity = cosine_similarity(Y_normalized.T)  # Độ tương đồng người dùng

    # In ra ma trận tương đồng giữa các người dùng
    print("Ma trận tương đồng người dùng:\n", user_similarity)

    # Lấy danh sách người dùng tương tự
    similar_users = np.argsort(user_similarity[current_user_index])[::-1][1:5]
    print(f"Người dùng hiện tại: {current_user_id}, Chỉ số trong ma trận: {current_user_index}")
    print(f"Những người dùng tương tự: {similar_users}")

    recommended_movies = set()
    user_seen_movies = np.where(R[:, current_user_index] == 1)[0]
    print(f"Phim đã xem bởi người dùng hiện tại: {user_seen_movies}")

    # Gợi ý phim từ những người dùng tương tự
    for user in similar_users:
        user_seen_movies_sim = np.where(R[:, user] == 1)[0]
        print(f"Phim đã xem bởi người dùng tương tự {user}: {user_seen_movies_sim}")

        for movie_id in user_seen_movies_sim:
            if movie_id not in user_seen_movies:
                recommended_movies.add(movie_id)

    # Kiểm tra nếu không có phim nào được gợi ý
    if not recommended_movies:
        messages.info(request, "Không có phim nào để gợi ý.")
        return redirect("index")

    # Lấy thông tin phim từ cơ sở dữ liệu
    movie_list = Movie.objects.filter(id__in=recommended_movies)[:10]
    print(f"Phim được gợi ý: {recommended_movies}")

    return render(request, 'web/recommend.html', {'movie_list': movie_list})

def index(request):
    movies = Movie.objects.all()
    query = request.GET.get('q')
    if query:
        movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
    return render(request, 'web/list.html', {'movies': movies})

def detail(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("login")

    movies = get_object_or_404(Movie, id=movie_id)
    if request.method == "POST":
        rate = request.POST['rating']
        ratingObject = Myrating(user=request.user, movie=movies, rating=rate)
        ratingObject.save()
        messages.success(request, "Đánh giá của bạn đã được ghi nhận.")
        return redirect("index")

    return render(request, 'web/detail.html', {'movies': movies})

def signUp(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect("index")
    return render(request, 'web/signUp.html', {'form': form})

def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect("index")
        else:
            return render(request, 'web/login.html', {'error_message': 'Thông tin đăng nhập không chính xác.'})
    return render(request, 'web/login.html')

def Logout(request):
    logout(request)
    return redirect("login")
