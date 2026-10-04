import pytest

from src.user_stats import stats
from src.config import ConfigManager


@pytest.fixture(autouse=True)
def clean_global_state():
    original_words_dir = ConfigManager.WORDS_DIR
    stats.reset()
    ConfigManager.clear_instances()
    yield
    stats.reset()
    ConfigManager.clear_instances()
    ConfigManager.WORDS_DIR = original_words_dir
