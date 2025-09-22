options_content = """\n
# --- User-editable configuration ---
# This file should contain user-specific configurations.
# This file will be imported in the main file while running
# either with WEB UI or CLI and should not run any long process
# by itself.
# DATA SETTINGS
from pathlib import Path
ROOT = Path("./input")  # Root directory for data
REAL_DF_FILENAME = "example.dta"  # Main data file name (must be .dta | .csv | .parquet | .xlsx)
OUTPUT_FOLDER = "Output"  # Output folder (None = default root/Output)
TARGET_NAME = "target"  # Name of the target column
# It is recommended to specify either NUMERICAL_COLS or CATEGORICAL_COLS to avoid ambiguity when inferring column types from your data.
NUMERICAL_COLS = None  # List of numerical columns (None = infer from data)
CATEGORICAL_COLS = None  # List of categorical columns (None = infer from data)
TEST_DF_SIZE = 1000  # Number of rows for test DataFrame
TEST_RATIO = 0.20  # Proportion of the dataset to include in the test split
# PIPELINE SETTINGS
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
SAMPLING_STRATEGY = "auto"  # SMOTE sampling strategy ('auto' recommended)
STRATIFY = True  # Whether to stratify the data
RANDOM_STATE = 42  # Random state for reproducibility
# You may define a custom pipeline here and use it in the options
# user_pipeline = ImbPipeline([
#     ("preprocessor", StandardScaler()),
#     ("smote", SMOTE(random_state=42)),
#     # Add more steps as needed
# ])
# MODEL/SEARCH SETTINGS
N_SPLITS = 5  # Cross-validation splits
SEARCH_TYPE = "random"  # or "grid"
SEARCH_KWARGS = {"verbose": 1}
# OUTPUT/PLOT SETTINGS
SHAP_PLOTS = False  # Enable SHAP plots
SHAP_SAMPLE_SIZE = 100  # Number of samples for SHAP plots
ROC_PLOTS = True  # Enable ROC plots
FEATURE_IMPORTANCES = True 
# DEBUG/TEST SETTINGS
TEST_MODE = False  # Enable test mode for quick runs
DEBUG = False  # Enable debug mode for extra checks
# --- Build Options object ---
from spml2 import Options
from models_user import models
options = Options(
    test_mode=TEST_MODE,
    debug=DEBUG,
    target_name=TARGET_NAME,
    test_df_size=TEST_DF_SIZE,
    test_ratio=TEST_RATIO,
    root=ROOT,
    real_df_filename=REAL_DF_FILENAME,
    output_folder=OUTPUT_FOLDER,
    numerical_cols=NUMERICAL_COLS,
    categorical_cols=CATEGORICAL_COLS,
    sampling_strategy=SAMPLING_STRATEGY,
    n_splits=N_SPLITS,
    shap_plots=SHAP_PLOTS,
    roc_plots=ROC_PLOTS,
    shap_sample_size=SHAP_SAMPLE_SIZE,
    pipeline=None,  # user_pipeline
    search_type=SEARCH_TYPE,
    search_kwargs=SEARCH_KWARGS,
    random_state=RANDOM_STATE,
    stratify=STRATIFY,
    feature_importances=FEATURE_IMPORTANCES,
)
print(options)
"""
