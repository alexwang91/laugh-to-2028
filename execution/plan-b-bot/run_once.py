import json

from beta_bot.config import Settings
from beta_bot.service import run_strategy


if __name__ == "__main__":
    print(json.dumps(run_strategy(Settings.from_env()), indent=2, ensure_ascii=False))
