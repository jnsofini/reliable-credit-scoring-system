# You can change the data storage location
# If you don't change it the code will saved in the default value
# Folder to store your data:

# Packages
import os
from pathlib import Path

# =============WHat you should change is this storage location
data_storage = "data/artifacts"
#
# ==========================================================


root_path = str(Path(os.path.abspath(os.path.dirname(__file__))).parent)
# print(p+"/test")
# ===========================================================
# DON'T CHANGE ANYTHING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING
RAW_DATA_BASE_PATH = (
    "/home/fini/Learning/CreditRisk/crm-simple-scorecard/mlops-model/data"
)

data_local_path = (
    "/home/fini/github-projects/mlops/capstone/data/heloc_dataset_v1.parquet"
)
BINNING_TRANSFORM_PATH = "binning-transformer.pkl"
TRANSFORM_DATA_PATH = "transform-data.parquet"
BASE_PATH = f"{root_path}/{data_storage}/"

# =============== RSPS PATHs for internal RSPS Benchmark model =============================================
BENCHMARK_DATA_BASE_PATH = "/home/modelling/projects/scorecard-model-pipeline/data"
RSPS_RAW_NON_ALC_DATA_BASE_PATH = f"{BENCHMARK_DATA_BASE_PATH}/RSPS/has_rsps"

# =============== ERS PATHs for Equifax ERS Benchmark model =============================================
ERS_RAW_ALNC_DATA_BASE_PATH = f"{BENCHMARK_DATA_BASE_PATH}/equifax/has_ers"
ERS_RAW_NON_ALC_DATA_BASE_PATH = f"{BENCHMARK_DATA_BASE_PATH}/equifax/has_ers"
ERS_RAW_DATA_BASE_PATH = f"{BENCHMARK_DATA_BASE_PATH}/equifax/has_ers"
