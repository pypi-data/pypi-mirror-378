import torch
import os  
from importlib import resources


def load_model():
    # Optional: allow users to override model via environment variable
    env_path = os.environ.get("EXSO_MODEL_PATH")
    if env_path and os.path.exists(env_path):
        return torch.load(env_path)

    # Load model from package
    with resources.path("exso_sdk.model", "exoplanet_model.pth") as model_path:
        return torch.load(model_path)

REQUIRED_COLUMNS = [
    'koi_period', 'koi_time0bk', 'koi_duration', 'koi_depth', 'koi_prad',
    'koi_sma', 'koi_incl', 'koi_teq', 'koi_insol', 'koi_srho', 'koi_srad',
    'koi_smass', 'koi_steff', 'koi_slogg', 'koi_smet', 'koi_model_snr'
]