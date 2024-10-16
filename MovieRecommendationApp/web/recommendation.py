import numpy as np
import pandas as pd
from web.models import Myrating, Movie
import scipy.optimize

def normalizeRatings(myY, myR):
    Ymean = np.sum(myY, axis=1) / np.sum(myR, axis=1)
    Ymean = Ymean.reshape((Ymean.shape[0], 1))
    return myY - Ymean, Ymean

def flattenParams(myX, myTheta):
    return np.concatenate((myX.flatten(), myTheta.flatten()))

def reshapeParams(flattened_XandTheta, mynm, mynu, mynf):
    reX = flattened_XandTheta[:int(mynm * mynf)].reshape((mynm, mynf))
    reTheta = flattened_XandTheta[int(mynm * mynf):].reshape((mynu, mynf))
    return reX, reTheta

def cofiCostFunc(myparams, myY, myR, mynu, mynm, mynf, mylambda=0.):
    myX, myTheta = reshapeParams(myparams, mynm, mynu, mynf)
    term1 = np.multiply(myX.dot(myTheta.T), myR)
    cost = 0.5 * np.sum(np.square(term1 - myY))
    cost += (mylambda / 2.) * (np.sum(np.square(myTheta)) + np.sum(np.square(myX)))
    return cost

def cofiGrad(myparams, myY, myR, mynu, mynm, mynf, mylambda=0.):
    myX, myTheta = reshapeParams(myparams, mynm, mynu, mynf)
    term1 = np.multiply(myX.dot(myTheta.T) - myY, myR)
    Xgrad = term1.dot(myTheta) + mylambda * myX
    Thetagrad = term1.T.dot(myX) + mylambda * myTheta
    return flattenParams(Xgrad, Thetagrad)

def Myrecommend(current_user_id):
    df = pd.DataFrame(list(Myrating.objects.all().values()))
    if df.empty:
        return []

    mynu = df.user_id.nunique()
    mynm = df.movie_id.nunique()
    mynf = 10

    Y = np.zeros((mynm, mynu))
    for row in df.itertuples():
        Y[row[2] - 1, row[4] - 1] = row[3]
    R = (Y != 0).astype(int)

    Ynorm, Ymean = normalizeRatings(Y, R)

    X = np.random.rand(mynm, mynf)
    Theta = np.random.rand(mynu, mynf)

    myflat = flattenParams(X, Theta)

    result = scipy.optimize.fmin_cg(
        cofiCostFunc, x0=myflat, fprime=cofiGrad,
        args=(Y, R, mynu, mynm, mynf, 12.2), maxiter=40, disp=True, full_output=True
    )

    resX, resTheta = reshapeParams(result[0], mynm, mynu, mynf)

    prediction_matrix = resX.dot(resTheta.T)

    user_index = current_user_id - 1
    user_predictions = prediction_matrix[:, user_index] + Ymean.flatten()

    user_ratings = Y[:, user_index]
    unseen_movie_indices = np.where(user_ratings == 0)[0]

    recommended_indices = unseen_movie_indices[np.argsort(user_predictions[unseen_movie_indices])[::-1]]

    recommended_movies = Movie.objects.filter(id__in=(recommended_indices + 1))[:10]

    return recommended_movies
