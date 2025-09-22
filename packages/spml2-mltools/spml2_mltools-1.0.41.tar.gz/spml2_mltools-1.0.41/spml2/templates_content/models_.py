models_content = """\n
# This file should contain user-specific models.
# This file will be imported in the main file while running
# either with WEB UI or CLI and should not run any long process
# by itself.
# Use 'include': True/False to control pipeline inclusion.
# For imbalanced data, consider metrics like PR AUC, MCC, and minority class recall.
import numpy as np
from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    StratifiedKFold,
    RandomizedSearchCV,
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    confusion_matrix,
    classification_report,
    recall_score,  # For minority class recall
)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings("ignore")
models = {
    "XGBoost": {
        "include": True,
        "model": XGBClassifier(random_state=42, n_jobs=-1, eval_metric="auc"),
        "params": {
            "model__n_estimators": [10, 50, 100, 200, 400, 750, 1000],
            "model__learning_rate": [0.001, 0.01, 0.1, 1, 10, 100],
            "model__max_depth": [3, 5, 7, 11, 15, 20, 30, 50],
            "model__colsample_bytree": [0.7, 0.9],
            "model__gamma": [0, 0.1],
            "model__reg_alpha": [0, 0.1],
            "model__reg_lambda": [0, 0.1],
            "model__scale_pos_weight": [1, 3],
        },
    },
    "RandomForest": {
        "include": True,
        "model": RandomForestClassifier(random_state=42, n_jobs=-1),
        "params": {
            "model__n_estimators": [100, 200, 300, 500],
            "model__criterion": ["gini", "entropy"],
            "model__max_depth": [None, 5, 10, 20],
            "model__min_samples_split": [2, 5, 10, 20],
            "model__min_samples_leaf": [1, 2, 4, 8],
            "model__class_weight": [None, "balanced"],
            "model__max_features": ["sqrt", "log2", None],
        },
    },
    "LogisticRegression-L2": {
        "include": True,
        "model": LogisticRegression(random_state=42, n_jobs=-1, max_iter=2000),
        "params": {
            "model__penalty": ["l2"],
            "model__C": [0.001, 0.01, 0.1, 1, 10],
            "model__solver": ["lbfgs", "saga", "newton-cg"],
            "model__class_weight": ["balanced"],
            "model__max_iter": [1000],
            "model__tol": [0.0001, 0.001],
        },
    },
    "LogisticRegression-L1": {
        "include": True,
        "model": LogisticRegression(random_state=42, n_jobs=-1, max_iter=2000),
        "params": {
            "model__penalty": ["l1"],
            "model__C": [0.001, 0.01, 0.1, 1, 10],
            "model__solver": ["saga"],
            "model__class_weight": ["balanced"],
            "model__max_iter": [1000],
        },
    },
    "KNN": {
        "include": True,
        "model": KNeighborsClassifier(n_jobs=-1),
        "params": {
            "model__n_neighbors": [3, 5, 7],
            "model__weights": ["uniform", "distance"],
            "model__p": [1, 2],
        },
    },
    "NaiveBayes": {
        "include": True,
        "model": GaussianNB(),
        "params": {"model__var_smoothing": np.logspace(-12, -6, 4)},
    },
    "SGDClassifier": {
        "include": True,
        "model": SGDClassifier(random_state=42, loss="log_loss", penalty="elasticnet"),
        "params": {
            "model__eta0": [0.001, 0.01, 0.1],
            "model__alpha": [0.0001, 0.001, 0.01],
            "model__l1_ratio": [0.15, 0.5, 0.85],
            "model__max_iter": [1000, 2000],
            "model__learning_rate": ["optimal", "adaptive"],
        },
    },
    "LogisticRegression-L2-EXCLUDE": {  # Example excluded model
        "include": False,
        "model": LogisticRegression(random_state=42, n_jobs=-1, max_iter=1000),
        "params": {
            "model__C": [0.001, 0.01, 0.1, 1, 10],
            "model__solver": ["lbfgs"],
            "model__class_weight": ["balanced"],
            "model__max_iter": [1000],
        },
    },
}
"""
