import os
import warnings

try:
    with open(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), '.version'), 'rt'
    ) as fid:
        __version__ = fid.readline().strip()
except FileNotFoundError:
    warnings.warn('.version file could not be found', stacklevel=1)
    __version__ = '0.0.0+dev'

# Define the public API.
from .main import (
    DSVenvConfig,
    EnvironmentType,
    create_env,
    initialize_venv,
)
