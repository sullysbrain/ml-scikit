import numpy as np
import pandas as pd
import scipy.stats
import sklearn
import xgboost 

class FixableDataFrame(pd.DataFrame):
    """ Helper class for manipulating generative models """
    def __init__(self, *args, fixed={}, **kwargs):
        self.__dict__["__fixed_var_dictionary"] = fixed
        super(FixableDataFrame, self).__init__(*args, **kwargs)
    def __setitem__(self, key, value):
        out = super(FixableDataFrame, self).__setitem__(key, value)
        if isinstance(key, str) and key in self.__dict__["__fixed_var_dictionary"]:
            out = super(FixableDataFrame, self).__setitem__(key, self.__dict__["__fixed_var_dictionary"][key])
        return out

# Generate the data
def generator(n, fixed={}, seed=0):
    if seed is not None:
        np.random.seed(seed)
    X = FixableDataFrame(fixed=fixed)
    X["Sales calls"] = np.random.uniform(0, 4, size=(n,)).round()
    X["Interactions"] = X["Sales calls"] + np.random.poisson(0.2, size=(n,))
    X["Economy"] = np.random.uniform(0, 1, size=(n,))
    X["Last upgrade"] = np.random.uniform(0, 20, size=(n,))
    X["Product need"] = (X["Sales calls"] * 0.1 + np.random.normal(0, 1, size=(n,)))
    X["Discount"] = ((1-scipy.special.expit(X["Product need"])) * 0.5 + 0.5 * np.random.uniform(0, 1, size=(n,))) / 2
    X["Monthly usage"] = scipy.special.expit(X["Product need"] * 0.3 + np.random.normal(0, 1, size=(n,)))
    X["Ad spend"] = X["Monthly usage"] * np.random.uniform(0.19, 0.9, size=(n,)) + (X["Last upgrade"] < 1) + (X["Last upgrade"] < 2)
    X["Bugs faced"] = np.array([np.random.poisson(v*2) for v in X["Monthly usage"]])
    X["Bugs reported"] = (X["Bugs faced"] * scipy.special.expit(X["Product need"])).round()
    X["Did renew"] = scipy.special.expit(7 * (
          0.18 * X["Product need"] \
        + 0.08 * X["Monthly usage"] \
        + 0.1 * X["Economy"] \
        + 0.05 * X["Discount"] \
        + 0.05 * np.random.normal(0, 1, size=(n,)) \
        + 0.05 * (1 - X['Bugs faced'] / 20) \
        + 0.005 * X["Sales calls"] \
        + 0.015 * X["Interactions"] \
        + 0.1 / (X["Last upgrade"]/4 + 0.25)
        + X["Ad spend"] * 0.0 - 0.45
    ))
    X["Did renew"] = scipy.stats.bernoulli.rvs(X["Did renew"])
    return X

def user_retention_dataset():
    n = 5000
    X_full = generator(n)
    y = X_full["Did renew"]
    X = X_full.drop(["Did renew", "Product need", "Bugs faced"], axis=1)
    return X,y

def fit_xgboost(X, y):
    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size=0.3)
    dtrain = xgboost.DMatrix(X_train, label=y_train)
    dtest = xgboost.DMatrix(X_test, label=y_test)
    model = xgboost.train({"eta": 0.001, "subsample": 0.5, "max_depth": 2, "objective": "reg:logistic"}, dtrain, 1000,num_boost_round=200000, evals=[(dtest, "test")], early_stopping_rounds=25, verbose_eval=False)
    return model

X, y = user_retention_dataset()
model = fit_xgboost(X, y)


## The SHAP values for a single sample
import shap
explainer = shap.Explainer(model)
shap_values = explainer(X)
clust = shap.utils.hclust(X, y, linkage="single")
shap.plots.bar(shap_values, clustering=clust, clustering_cutoff=1)

shap.plots.scatter(shap_values, ylabel="SHAP value\n(higher means more likely to renew)")

