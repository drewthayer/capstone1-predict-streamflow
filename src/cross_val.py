from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
import numpy as np

def cross_val(X, y, model, n_folds, errortype='RMSE', random_seed=154):
    """Estimate the in- and out-of-sample error of a model using cross
    validation.

    Requirements
    ----------
    #class XyScaler
    function rmsle

    Parameters
    ----------

    X: np.array
      Matrix of predictors, standardized

    y: np.array
      Target array, standardized

    model: sklearn model object.
      The estimator to fit.  Must have fit and predict methods.

    n_folds: int
      The number of folds in the cross validation.

    errortype: string
      either 'RMSE' or 'RMSLE'

    random_seed: int
      A seed for the random number generator, for repeatability.

    Returns
    -------

    errors, cfs_best: tuple of arrays
    errors = (train errors, test errors) for each fold of cross-validation
    cfs-best = coefficients selected from minimum test error
    """
    # choose KFolds or TimeSeriesSplit
    kf = TimeSeriesSplit(n_splits=n_folds)
    #kf = KFold(n_folds, random_state=random_seed)
    errorlist = []
    cfs = []
    for k, (train_index,test_index) in enumerate(kf.split(X)):
        # define variables
        X_train = X[train_index]
        y_train = y[train_index]
        X_test = X[test_index]
        y_test = y[test_index]
        # fit model
        model.fit(X_train,y_train)
        y_hat_train = model.predict(X_train)
        # predict based on test data 
        y_hat_test = model.predict(X_test)
        # evaluate model
        if errortype == 'RMSE':
            rmse_train = np.sqrt(mean_squared_error(y_hat_train,y_train))
            rmse_test = np.sqrt(mean_squared_error(y_hat_test,y_test))
            errorlist.append((rmse_train, rmse_test)) # tuple output
        elif errortype == 'RMSLE':
            rmsle_train = rmsle(y_train, y_hat_train)
            rmsle_test = rmsle(y_test, y_hat_test)
            errorlist.append((rmsle_train, rmsle_test)) # tuple output
        # store coefficients
        cfs.append (model.coef_)
    # select best coefficients
    errors = np.asarray(errorlist)
    idx_min_test_error = errors[:,1].argmin()
    cfs_best = cfs[idx_min_test_error]

    return(errors, cfs_best)
