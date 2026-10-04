from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

from src.exceptions import ConfigLoadError, InvalidProductCategoryError


class ConfigManager:
    """Load, cache, and reload category-specific word configuration."""

    _instances: ClassVar[dict[str, ConfigManager]] = {}

    WORDS_DIR: ClassVar[Path] = (
        Path(__file__).resolve().parents[2] / "config_files" / "words"
    )

    _product_category: str
    _words_cache: dict[str, tuple[str, ...]] | None
    _file_mtimes: int | None

    def __new__(cls, product_category: str) -> ConfigManager:
        """Return one cached manager instance per product category."""
        if not isinstance(product_category, str):
            raise InvalidProductCategoryError(product_category)
        key = product_category.strip().lower()
        if not key or Path(key).name != key:
            raise InvalidProductCategoryError(product_category)

        instance = cls._instances.get(key)
        if instance is None:
            instance = super().__new__(cls)
            instance._product_category = key
            instance._words_cache = None
            instance._file_mtimes = None
            cls._instances[key] = instance
        return instance

    def _get_file_paths(self) -> set[Path]:
        """Return the general and category-specific configuration paths."""
        return {
            self.WORDS_DIR / "general.json",
            self.WORDS_DIR / f"{self._product_category}.json",
        }

    def _get_file_mtimes(self) -> int:
        """Return a value that changes when any configuration file changes."""
        markers = []
        for path in sorted(self._get_file_paths()):
            try:
                info = path.stat()
            except OSError as exc:
                raise ConfigLoadError(str(path), f"cannot read file ({exc})") from exc
            # size is included because some file systems have coarse timestamps
            markers.append((str(path), info.st_mtime_ns, info.st_size))
        return hash(tuple(markers))

    @staticmethod
    def _load_file(file_path: Path) -> dict[str, list[str]]:
        """Load and validate one JSON configuration file."""
        path = Path(file_path)
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ConfigLoadError(str(path), f"cannot read file ({exc})") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConfigLoadError(str(path), f"invalid JSON ({exc})") from exc

        if not isinstance(data, dict):
            raise ConfigLoadError(str(path), "JSON root must be an object")

        for key in ("reject_words", "review_words"):
            value = data.get(key)
            if not isinstance(value, list) or not all(isinstance(w, str) for w in value):
                raise ConfigLoadError(str(path), f"'{key}' must be a list of strings")

        return {key: data[key] for key in ("reject_words", "review_words")}

    def _load_words(self) -> dict[str, tuple[str, ...]]:
        """Load general and category-specific words into the cache."""
        marker = self._get_file_mtimes()
        general = self._load_file(self.WORDS_DIR / "general.json")
        category = self._load_file(self.WORDS_DIR / f"{self._product_category}.json")

        words = {
            key: tuple(dict.fromkeys(general[key] + category[key]))
            for key in ("reject_words", "review_words")
        }
        self._words_cache = words
        self._file_mtimes = marker
        return words

    def _get_words(self) -> dict[str, tuple[str, ...]]:
        """Return cached words, reloading when configuration files change."""
        current_mtimes = self._get_file_mtimes()
        if self._words_cache is None or self._file_mtimes != current_mtimes:
            return self._load_words()
        return self._words_cache

    @property
    def reject_words(self) -> tuple[str, ...]:
        """Return words that cause automatic rejection."""
        return self._get_words()["reject_words"]

    @property
    def review_words(self) -> tuple[str, ...]:
        """Return words that require human review."""
        return self._get_words()["review_words"]

    def reload(self) -> None:
        """Invalidate this category's cached configuration."""
        self._words_cache = None
        self._file_mtimes = None

    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached manager instances."""
        cls._instances.clear()