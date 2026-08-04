"""Compatibility entry point for the frozen V1 rotation backtest.

The canonical implementation lives in research/core/crypto_rotation_backtest.py.
"""

from core.crypto_rotation_backtest import *  # noqa: F401,F403


if __name__ == "__main__":
    main()
