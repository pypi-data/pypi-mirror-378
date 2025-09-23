#!/usr/bin/env python3
"""Core helpers for the vexy_markliff package."""
# this_file: src/vexy_markliff/vexy_markliff.py

import logging
from collections import Counter
from dataclasses import dataclass
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Minimal configuration container used by ``process_data``."""

    name: str
    value: str | int | float
    options: dict[str, Any] | None = None


def process_data(
    data: list[Any],
    config: Config | None = None,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Normalize list data and provide a lightweight summary."""

    if not isinstance(data, list):
        msg = "data must be provided as a list"
        raise TypeError(msg)

    original_level = logger.level
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    try:
        normalized: list[str] = []
        for item in data:
            text = str(item).strip()
            if text:
                normalized.append(text)

        if not normalized:
            msg = "input data must contain at least one non-empty item"
            raise ValueError(msg)

        frequencies = Counter(normalized)
        unique_count = len(frequencies)
        result: dict[str, Any] = {
            "items": normalized,
            "summary": {"total": len(normalized), "unique": unique_count},
            "count": len(normalized),
            "unique": unique_count,
            "frequency": dict(frequencies),
        }

        if config:
            result["config"] = {
                "name": config.name,
                "value": config.value,
                "options": config.options or {},
            }

        logger.debug("Processed data result: %s", result)
        return result
    finally:
        if debug:
            logger.setLevel(original_level)


def main() -> None:
    """Main entry point for vexy_markliff."""
    try:
        config = Config(name="default", value="demo", options={"mode": "summary"})
        sample_data = [" alpha ", "beta", "alpha"]
        result = process_data(sample_data, config=config, debug=True)
        logger.info("Processing completed: %s", result)

    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        raise


if __name__ == "__main__":
    main()
