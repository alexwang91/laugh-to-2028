from __future__ import annotations

import json
import os

from beta_bot.config import Settings
from beta_bot.emergency import EmergencyController, NewRiskKillSwitch, kill_switch_path


def main() -> None:
    settings = Settings.from_env()
    action = (os.getenv("EMERGENCY_ACTION") or "").strip().lower()
    reason = (os.getenv("EMERGENCY_REASON") or "operator_emergency_switch").strip()

    if action == "disable-new-risk":
        result = NewRiskKillSwitch(kill_switch_path(settings)).disable(reason=reason)
        print(json.dumps({"action": action, "result": result}, sort_keys=True))
        return

    controller = EmergencyController(settings)
    if action == "cancel-all":
        actions = controller.cancel_all()
    elif action == "reduce-only-close":
        actions = controller.reduce_only_close()
    elif action == "emergency-flat":
        actions = controller.emergency_flat()
    else:
        raise SystemExit(
            "EMERGENCY_ACTION must be one of: cancel-all, reduce-only-close, emergency-flat, disable-new-risk"
        )
    print(json.dumps({"action": action, "result": [item.to_dict() for item in actions]}, sort_keys=True))


if __name__ == "__main__":
    main()
