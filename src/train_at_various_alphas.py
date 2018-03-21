def train_at_various_alphas(X, y, model, alphas, n_folds=10, errortype='RMSE', **kwargs):
    """Train a regularized regression model using cross validation at various
    values of alpha.

    requirements
    ----------
    class XyScaler
    function rmsle
    function cross_val

    Parameters
    ----------

    X: np.array
      Matrix of predictors, standardized

    y: np.array
      Target array, standardized

    model: name of sklearn model class
      A class in sklearn that can be used to create a regularized regression
      object.  Options are 'Ridge' and 'Lasso'.

    alphas: numpy array
      An array of regularization parameters.

    n_folds: int
      Number of cross validation folds.

    errortype: string
      either 'RMSE' or 'RMSLE'

    Returns
    -------

    cv_errors_train, cv_errors_test: tuple of DataFrame
      DataFrames containing the training and testing errors for each value of
      alpha and each cross validation fold.  Each row represents a CV fold, and
      each column a value of alpha.

      Dataframe containing coefficients for each parameter for each alpha
    """
    cv_errors_train = pd.DataFrame(np.empty(shape=(n_folds, len(alphas))),
                                     columns=alphas)
    cv_errors_test = pd.DataFrame(np.empty(shape=(n_folds, len(alphas))),
                                        columns=alphas)
    coefs_df = pd.DataFrame(np.empty(shape=(n_folds, len(alphas))),
                                        columns=alphas)
    for idx, alpha in enumerate(alphas):
        errors, coefs = cross_val(X, y, model(alpha), n_folds, errortype='RMSE', random_seed=154)
        cv_errors_train.iloc[:,idx] = errors[:,0]
        cv_errors_test.iloc[:,idx] = errors[:,1]
        #coefs_df.iloc[:,idx] = coefs
    return(cv_errors_train, cv_errors_test)#, coefs_df
