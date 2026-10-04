import json
from pathlib import Path

import pytest

from src.config import ConfigManager
from src.exceptions import ConfigLoadError


def make_config_dir(tmp_path: Path, general_data=None, category_data=None):
    words = tmp_path / "words"
    words.mkdir()
    (words / "general.json").write_text(
        json.dumps(general_data or {"reject_words": ["bad"], "review_words": ["flag"]}),
        encoding="utf-8",
    )
    (words / "clothing.json").write_text(
        json.dumps(category_data or {"reject_words": ["cloth_bad"], "review_words": ["cloth_flag"]}),
        encoding="utf-8",
    )
    return words


def test_load_and_cache(tmp_path):
    words = make_config_dir(tmp_path)
    ConfigManager.WORDS_DIR = words
    config = ConfigManager("Clothing")
    assert config is ConfigManager("clothing")
    assert sorted(config.reject_words) == ["bad", "cloth_bad"]
    assert sorted(config.review_words) == ["cloth_flag", "flag"]
    assert config.reject_words is config.reject_words


def test_reload_clears_cache(tmp_path):
    words = make_config_dir(tmp_path)
    ConfigManager.WORDS_DIR = words
    config = ConfigManager("clothing")
    assert sorted(config.reject_words) == ["bad", "cloth_bad"]
    config.reload()
    assert sorted(config.reject_words) == ["bad", "cloth_bad"]


def test_changed_file_reloads(tmp_path):
    words = make_config_dir(tmp_path)
    ConfigManager.WORDS_DIR = words
    config = ConfigManager("clothing")
    assert sorted(config.reject_words) == ["bad", "cloth_bad"]
    path = words / "clothing.json"
    path.write_text(
        json.dumps({"reject_words": ["new"], "review_words": []}),
        encoding="utf-8",
    )
    assert sorted(config.reject_words) == ["bad", "new"]


def test_missing_category_file(tmp_path):
    words = tmp_path / "words"
    words.mkdir()
    (words / "general.json").write_text(
        json.dumps({"reject_words": [], "review_words": []}), encoding="utf-8"
    )
    ConfigManager.WORDS_DIR = words
    with pytest.raises(ConfigLoadError):
        ConfigManager("clothing").reject_words


@pytest.mark.parametrize(
    "content",
    [
        "{",
        "[]",
        json.dumps({"reject_words": []}),
        json.dumps({"reject_words": [], "review_words": "bad"}),
    ],
)
def test_invalid_config_content(tmp_path, content):
    words = tmp_path / "words"
    words.mkdir()
    for name in ("general.json", "clothing.json"):
        (words / name).write_text(content, encoding="utf-8")
    ConfigManager.WORDS_DIR = words
    with pytest.raises(ConfigLoadError):
        ConfigManager("clothing").reject_words


def test_clear_instances():
    first = ConfigManager("clothing")
    ConfigManager.clear_instances()
    second = ConfigManager("clothing")
    assert first is not second


def test_load_file_missing_directly(tmp_path):
    with pytest.raises(ConfigLoadError):
        ConfigManager._load_file(tmp_path / "missing.json")

def test_diffrent_class(tmp_path):
    words = make_config_dir(tmp_path)
    ConfigManager.WORDS_DIR = words
    path = words / "electronics.json"
    path.write_text(
        json.dumps({"reject_words": ["new"], "review_words": []}),
        encoding="utf-8",
    )
    config_clothing = ConfigManager("clothing")
    assert config_clothing is ConfigManager("clothing")
    config_electronics = ConfigManager("electronics")
    assert config_electronics is ConfigManager("electronics")
    assert config_clothing is not config_electronics
    assert sorted(config_clothing.reject_words) != sorted(config_electronics.reject_words)