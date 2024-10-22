import numpy as np  # Nhập thư viện NumPy để làm việc với mảng và tính toán số học.
import pandas as pd  # Nhập thư viện pandas để làm việc với dữ liệu dạng bảng.
from web.models import Myrating, Movie  # Nhập các mô hình Myrating và Movie từ ứng dụng web.
import scipy.optimize  # Nhập thư viện scipy.optimize để sử dụng các hàm tối ưu hóa.

def normalizeRatings(myY, myR):
    # Chuẩn hóa đánh giá bằng cách trừ đi giá trị trung bình từ mỗi hàng.
    Ymean = np.sum(myY, axis=1) / np.sum(myR, axis=1)  # Tính giá trị trung bình cho mỗi phim.
    Ymean = Ymean.reshape((Ymean.shape[0], 1))  # Chuyển đổi thành mảng 2D.
    return myY - Ymean, Ymean  # Trả về ma trận đánh giá đã chuẩn hóa và giá trị trung bình.

def flattenParams(myX, myTheta):
    # Gộp các ma trận X và Theta thành một mảng phẳng.
    return np.concatenate((myX.flatten(), myTheta.flatten()))

def reshapeParams(flattened_XandTheta, mynm, mynu, mynf):
    # Chuyển đổi mảng phẳng thành các ma trận X và Theta.
    reX = flattened_XandTheta[:int(mynm * mynf)].reshape((mynm, mynf))  # Reshape X.
    reTheta = flattened_XandTheta[int(mynm * mynf):].reshape((mynu, mynf))  # Reshape Theta.
    return reX, reTheta  # Trả về hai ma trận đã được reshape.

def cofiCostFunc(myparams, myY, myR, mynu, mynm, mynf, mylambda=0.):
    # Tính toán chi phí cho thuật toán Collaborative Filtering.
    myX, myTheta = reshapeParams(myparams, mynm, mynu, mynf)  # Reshape tham số.
    term1 = np.multiply(myX.dot(myTheta.T), myR)  # Tính phần 1 của chi phí.
    cost = 0.5 * np.sum(np.square(term1 - myY))  # Tính chi phí dựa trên đánh giá thực tế.
    cost += (mylambda / 2.) * (np.sum(np.square(myTheta)) + np.sum(np.square(myX)))  # Thêm phần regularization.
    return cost  # Trả về chi phí tổng.

def cofiGrad(myparams, myY, myR, mynu, mynm, mynf, mylambda=0.):
    # Tính toán gradient cho thuật toán Collaborative Filtering.
    myX, myTheta = reshapeParams(myparams, mynm, mynu, mynf)  # Reshape tham số.
    term1 = np.multiply(myX.dot(myTheta.T) - myY, myR)  # Tính phần 1 cho gradient.
    Xgrad = term1.dot(myTheta) + mylambda * myX  # Tính gradient cho X.
    Thetagrad = term1.T.dot(myX) + mylambda * myTheta  # Tính gradient cho Theta.
    return flattenParams(Xgrad, Thetagrad)  # Gộp và trả về gradient.

def Myrecommend(current_user_id):
    # Hàm gợi ý phim cho người dùng hiện tại dựa trên đánh giá.
    df = pd.DataFrame(list(Myrating.objects.all().values()))  # Lấy dữ liệu từ Myrating và chuyển đổi thành DataFrame.
    if df.empty:  # Kiểm tra nếu DataFrame rỗng.
        return []  # Trả về danh sách rỗng nếu không có đánh giá.

    mynu = df.user_id.nunique()  # Số lượng người dùng duy nhất.
    mynm = df.movie_id.nunique()  # Số lượng phim duy nhất.
    mynf = 10  # Số lượng đặc trưng cho từng phim.

    Y = np.zeros((mynm, mynu))  # Tạo ma trận đánh giá.
    for row in df.itertuples():  # Duyệt qua từng hàng trong DataFrame.
        Y[row[2] - 1, row[4] - 1] = row[3]  # Gán đánh giá cho ma trận Y.
    R = (Y != 0).astype(int)  # Tạo ma trận R cho biết đánh giá có tồn tại hay không.

    Ynorm, Ymean = normalizeRatings(Y, R)  # Chuẩn hóa đánh giá và lấy giá trị trung bình.

    X = np.random.rand(mynm, mynf)  # Khởi tạo ngẫu nhiên ma trận X.
    Theta = np.random.rand(mynu, mynf)  # Khởi tạo ngẫu nhiên ma trận Theta.

    myflat = flattenParams(X, Theta)  # Gộp X và Theta thành mảng phẳng.

    # Tối ưu hóa chi phí bằng thuật toán tối ưu hóa.
    result = scipy.optimize.fmin_cg(
        cofiCostFunc, x0=myflat, fprime=cofiGrad,
        args=(Y, R, mynu, mynm, mynf, 12.2), maxiter=40, disp=True, full_output=True
    )

    resX, resTheta = reshapeParams(result[0], mynm, mynu, mynf)  # Reshape kết quả tối ưu hóa.

    prediction_matrix = resX.dot(resTheta.T)  # Tính toán ma trận dự đoán.

    user_index = current_user_id - 1  # Chuyển đổi ID người dùng thành chỉ số.
    user_predictions = prediction_matrix[:, user_index] + Ymean.flatten()  # Dự đoán đánh giá cho người dùng hiện tại.

    user_ratings = Y[:, user_index]  # Lấy đánh giá thực tế của người dùng.
    unseen_movie_indices = np.where(user_ratings == 0)[0]  # Tìm chỉ số phim chưa được xem.

    recommended_indices = unseen_movie_indices[np.argsort(user_predictions[unseen_movie_indices])[::-1]]  # Sắp xếp phim chưa xem theo dự đoán.

    recommended_movies = Movie.objects.filter(id__in=(recommended_indices + 1))[:10]  # Lấy 10 phim gợi ý từ cơ sở dữ liệu.

    return recommended_movies  # Trả về danh sách phim gợi ý.
