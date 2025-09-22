from abc import ABC, abstractmethod
import copy
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple, Dict
import time

#
import numpy as np
import pandas as pd
from rich import print
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    RandomizedSearchCV,
)
from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_curve,
)
from sklearn.compose import ColumnTransformer
from sklearn.metrics import matthews_corrcoef, average_precision_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.model_selection import GridSearchCV
from typing import Literal

#
from spml2.data.processing import assert_columns_exist, assert_numerical_cols
from spml2.models.base import models as DEFAULT_MODELS
from spml2.options import Options
from spml2.utils.general import (
    print_report_initial,
    initial_data_check,
    save_results_individual,
    save_results,
    save_model,
    get_data,
    check_cols,
    name_format_estimator,
    results_report,
    limited_models,
    save_pip_freeze,
    save_metrics,
    load_metrics_cache,
    load_model_cache,
    local_print,
    local_print_df,
)
from spml2.plots.plot_roc import plot_roc_curve
from spml2.feature_importances import (
    FeatureImportancesAbstract,
    FeatureImportancesBasic,
    FeatureImportancesSKLEARN,
    save_feature_df,
    save_feature_importances,
    save_feature_importances_basic,
    save_feature_importances_SKLEARN,
)

# / Local imports =============================================================
# ================Warnings=====================================================
warnings.filterwarnings("ignore")


# =================================Core Process================================
def get_search_type(
    options: Options, param_grid: dict
) -> RandomizedSearchCV | GridSearchCV:
    search_type = getattr(options, "search_type", "random")
    search_kwargs = (getattr(options, "search_kwargs", None) or {}).copy()
    default_kwargs = {
        "cv": StratifiedKFold(n_splits=options.n_splits, shuffle=True, random_state=42),
        "scoring": "roc_auc",
        "verbose": 1,
        "n_jobs": -1,
        "error_score": "raise",
    }
    search_kwargs.update(default_kwargs)
    if search_type == "random":
        search = RandomizedSearchCV(options.pipeline, param_grid, **search_kwargs)
    elif search_type == "grid":
        search = GridSearchCV(options.pipeline, param_grid, **search_kwargs)
    else:
        # fallback to random search
        search = RandomizedSearchCV(options.pipeline, param_grid, **search_kwargs)
    return search


def get_pipeline(options: Options, preprocessor: Any, model: Any) -> ImbPipeline:
    if isinstance(options.pipeline, ImbPipeline):
        options._given_pipeline = copy.deepcopy(options.pipeline)
    else:
        options._given_pipeline = None
    if options._given_pipeline is None:
        options.pipeline = ImbPipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "smote",
                    SMOTE(random_state=42, sampling_strategy=options.sampling_strategy),
                ),
                ("model", model),
            ]
        )
    else:
        steps = options.pipeline.steps
        if steps and steps[-1][0] == "model":
            steps[-1] = ("model", model)
        else:
            steps.append(("model", model))
        options.pipeline = ImbPipeline(steps)
    if not isinstance(options.pipeline, ImbPipeline):
        raise ValueError(
            f"Pipeline is not an instance of ImbPipeline. Got {type(options.pipeline)}"
        )
    return options


def check_pipeline(options: Options):
    assert isinstance(
        options.pipeline, ImbPipeline
    ), "Pipeline is not an instance of ImbPipeline"
    assert options.categorical_cols is not None
    assert options.numerical_cols is not None
    # print(options.categorical_cols, options.numerical_cols)


def fit_and_measure(search, X_train, y_train):
    start = datetime.now()
    search.fit(X_train, y_train)
    end = datetime.now()
    duration = end - start
    return duration


def train_and_search(
    model: Any,
    preprocessor: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    options: Options,
    param_grid: dict,
) -> tuple[Any, Any, dict]:
    options = get_pipeline(options, preprocessor, model)
    check_pipeline(options)
    search = get_search_type(options, param_grid)
    start = datetime.now()
    search.fit(X_train, y_train)
    end = datetime.now()
    duration = end - start
    # duration = fit_and_measure(search, X_train, y_train)
    return search.best_estimator_, duration, search.best_params_


def evaluate_model(
    model: Any, X_test: pd.DataFrame, y_test: pd.Series
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    y_pred = model.predict(X_test)
    try:
        y_proba = model.predict_proba(X_test)
        if y_proba.shape[1] == 2:
            y_proba = y_proba[:, 1]
    except AttributeError:
        try:
            y_proba = model.decision_function(X_test)
        except AttributeError:
            y_proba = None
    metrics = {
        "F1 Score": f1_score(
            y_test, y_pred, average="binary" if len(np.unique(y_test)) == 2 else "macro"
        ),
        "Confusion Matrix": confusion_matrix(y_test, y_pred),
        "Classification Report": classification_report(
            y_test, y_pred, output_dict=True
        ),
        "MCC": matthews_corrcoef(y_test, y_pred),
        "PR AUC": (
            average_precision_score(y_test, y_proba) if y_proba is not None else None
        ),
    }
    if y_proba is not None:
        try:
            metrics["ROC AUC"] = roc_auc_score(y_test, y_proba)
        except Exception:
            metrics["ROC AUC"] = None
    return y_pred, y_proba, metrics


class ActionAbstract:
    name: str = "ActionAbstract"
    description: str = "Abstract action"

    def __init__(
        self, options: Options, models: dict, output_area=None, plot_area=None
    ):
        self.options = options
        self.models = models
        self.output_area = output_area
        self.plot_area = plot_area

    def get_df(self):
        initial_data_check(self.options)
        df = get_data(self.options)
        return df

    def get_preprocessor(
        self, options: Options, categorical_cols: list
    ) -> ColumnTransformer:
        return ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), options.numerical_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ]
        )

    @abstractmethod
    def get_metrics(self, model, X_test, y_test): ...
    def get_result_name(self, model_name: str) -> str:
        result_name = name_format_estimator(model_name, self.df_final, self.options)
        if self.name != "Fresh":
            result_name = f"repeated_{result_name}"
        return result_name

    def shap_plots(self, model: Any, X: pd.DataFrame, result_name: str):
        if not self.options.shap_plots:
            return
        from spml2.plots.shap_local import ShapTree, ShapLinear, ShapAuto

        folder = self.options.output_folder / "graphs"
        folder.mkdir(parents=True, exist_ok=True)
        rows = self.options.shap_sample_size
        explainer = ShapAuto(model, X.head(rows), options=self.options)
        try:
            explainer.summary_plot(
                save_path=folder / f"shap_summary_{result_name}.png",
                plot_type=self.options.shap_summary_plot_type,
            )
        except Exception as e:
            if self.options.raise_error:
                raise e
            else:
                warnings.warn(f"Shap summary plot failed for {result_name}: {e}")

    def should_I_pass(self, model_name: str, config: dict[str, Any]) -> bool:
        if str(model_name).strip().startswith("#") or "cancelled" in model_name.lower():
            self.print(f"\nPassing {model_name}\n")
            return True
        if not config.get("include", True):
            self.print(f"\nPassing {model_name} as include is False\n")
            return True
        return False

    def test_name_when_debug(self, models: dict) -> str:
        if "XGBoost" in models:
            return "XGBoost"
        return list(models.keys())[0]

    def print(self, msg: str):
        local_print(msg, output_area=self.output_area)

    def execute(self) -> "ActionAbstract":
        from spml2.data.abstract import get_data_with_options, DataAbstract

        if self.name == "Fresh":
            save_pip_freeze(self.options)
        df = self.get_df()
        self.data_abstract: DataAbstract = get_data_with_options(
            self.options, df, self.output_area
        )
        X_train, X_test, y_train, y_test = self.data_abstract.get_X_y()
        self.df_final = self.data_abstract.df
        preprocessor = self.get_preprocessor(
            self.options, self.data_abstract.categorical_cols
        )
        features = X_train.columns.tolist()
        results = []
        for model_name, config in self.models.items():
            if self.should_I_pass(model_name, config):
                continue
            if self.options.debug:
                if model_name != self.test_name_when_debug(self.models):
                    self.print(f"Debug mode is open passing this {model_name}")
                    continue
            self.print(f"\n Next Model : {model_name} \n")
            best_model, duration, best_params = self.get_best_model(
                config, preprocessor, X_train, y_train, self.options, model_name
            )
            metrics = self.get_metrics(best_model, X_test, y_test)
            result_name = self.get_result_name(model_name)
            save_model(best_model, result_name, self.options)
            save_metrics(metrics, result_name, self.options)
            # Shap Summary plot
            if self.options.shap_plots:
                arr = best_model.named_steps["preprocessor"].transform(X_test)
                # Dynamically get feature names from the preprocessor
                feature_names = []
                for name, transformer, cols in best_model.named_steps[
                    "preprocessor"
                ].transformers_:
                    if name == "num":
                        feature_names += cols
                    elif name == "cat":
                        if hasattr(transformer, "get_feature_names_out"):
                            try:
                                feature_names += list(
                                    transformer.get_feature_names_out(cols)
                                )
                            except NotFittedError:
                                # Fallback: encoder not fitted, use original column names
                                feature_names += cols
                        else:
                            feature_names += cols
                X_test_processed = pd.DataFrame(arr, columns=feature_names)
                self.shap_plots(
                    best_model.named_steps["model"], X_test_processed, result_name
                )
            # ROC AUC plot
            if self.options.roc_plots:
                plot_roc_curve(
                    model_name,
                    best_model,
                    self.options,
                    X_test,
                    y_test,
                    out_name=result_name,
                    output_area=self.output_area,
                    plot_area=self.plot_area,
                )
            if duration is None:
                duration = " "
            else:
                rounded_seconds = round(duration.total_seconds())
                duration = f" : {rounded_seconds:.2f} seconds"
            self.print(f"\n{model_name}{duration} \n ")
            model_results_dict = {
                "Model": model_name,
                "Best Params": str(best_params),
                "ROC AUC": metrics.get("ROC AUC", None),
                "F1 Score": metrics.get("F1 Score", None),
                "MCC": metrics.get("MCC", None),
                "PR AUC": metrics.get("PR AUC", None),
                "Confusion Matrix": metrics.get("Confusion Matrix", None),
                "Classification Report": metrics.get("Classification Report", None),
                "Feature Importance": getattr(
                    best_model.named_steps["model"], "feature_importances_", None
                ),
                "duration": str(duration),
                "nf_estimator": result_name,
            }
            if self.options.feature_importances:
                save_feature_importances(
                    best_model,
                    self.options,
                    result_name,
                    features=features,
                    X_test=X_test,
                    y_test=y_test,
                    output_area=self.output_area,
                )
            model_results_df = pd.DataFrame([model_results_dict])
            print(model_results_df)
            save_results_individual(
                self.df_final,
                model_name,
                model_results_df,
                self.options,
            )
            results.append(model_results_dict)
        if self.name == "Fresh":
            results_report(
                results,
                self.df_final,
                self.options,
                output_area=self.output_area,
                plot_area=self.plot_area,
            )
        return self

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)


class ActionFresh(ActionAbstract):
    name = "Fresh"
    description = "Fresh data processing action"

    def get_best_model(
        self, config, preprocessor, X_train, y_train, options, model_name
    ):
        best_model, duration, best_params = train_and_search(
            config["model"], preprocessor, X_train, y_train, options, config["params"]
        )
        return best_model, duration, best_params

    def get_metrics(self, best_model, X_test, y_test):
        y_pred, y_proba, metrics = evaluate_model(best_model, X_test, y_test)
        return metrics


class ActionCache(ActionAbstract):
    name = "Cache"
    description = "Cache data processing action"

    def get_best_model(
        self, config, preprocessor, X_train, y_train, options, model_name
    ):
        self.print(f"\n[Checking cache] Next model : { model_name} \n")
        bucket_name = name_format_estimator(model_name, self.df_final, options)
        best_model = load_model_cache(bucket_name, options)
        self.metrics = load_metrics_cache(bucket_name, options)
        return best_model, None, None

    def get_metrics(self, best_model, X_test, y_test):
        return self.metrics


def Process(options: Options, models: dict, output_area=None, plot_area=None):
    return ActionFresh(
        options, models, output_area=output_area, plot_area=plot_area
    ).execute()


def Process_cache(options: Options, models: dict, output_area=None, plot_area=None):
    return ActionCache(
        options, models, output_area=output_area, plot_area=plot_area
    ).execute()
