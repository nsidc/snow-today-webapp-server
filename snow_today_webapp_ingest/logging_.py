from __future__ import annotations

import sys

import loguru


def setup_logger(logger: loguru.Logger, *, log_level: int = 20):
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.level("INFO", color="<white>")
