from pathlib import Path

# Repo root path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Config paths
CONFIGS_DIR = ROOT_DIR / "configs"
LANGUAGES_CONFIG = CONFIGS_DIR / "languages.yaml"
TOKENIZERS_CONFIG = CONFIGS_DIR / "tokenizers.yaml"
DATASETS_CONFIG = CONFIGS_DIR / "datasets.yaml"
PREPROCESSING_CONFIG = CONFIGS_DIR / "preprocessing.yaml"

# Data paths
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESULTS_DATA_DIR = DATA_DIR / "results"

# Research log paths
RESEARCH_LOG_DIR = ROOT_DIR / "research_log"
RUNS_LOG_DIR = RESEARCH_LOG_DIR / "runs"
REFLECTIONS_LOG_DIR = RESEARCH_LOG_DIR / "reflections"

# Report and paper paths
REPORT_DIR = ROOT_DIR / "report"
PAPER_DIR = ROOT_DIR / "paper"
