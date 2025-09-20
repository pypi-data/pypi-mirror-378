import os
import platform
import platformdirs
from pathlib import Path

OS_TYPE = None
if platform.system() == 'Windows':
    OS_TYPE = 'Windows'
elif platform.system() == 'Darwin':
    OS_TYPE = 'MacOS'
elif platform.system() == 'Linux':
    OS_TYPE = 'Linux'

LEANUP_CACHE_DIR = Path(
    os.getenv('LEANUP_CACHE_DIR', platformdirs.user_cache_dir("leanup")))

LEANUP_CONFIG_DIR = Path(
    os.getenv('LEANUP_CONFIG_DIR', platformdirs.user_config_dir("leanup")))

TMP_DIR = os.getenv("TMP_DIR")
if isinstance(TMP_DIR, str):
    TMP_DIR = Path(TMP_DIR)
