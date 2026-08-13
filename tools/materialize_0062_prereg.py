from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

OLD_TOOLING_COMMIT = "815e24f608273ab503ef1ef346ee6b10497ed29c"
OLD_SCRIPT_PATH = "tools/materialize_0062_prereg.py"


def main() -> None:
    root = Path.cwd()
    source = subprocess.check_output(
        ["git", "show", f"{OLD_TOOLING_COMMIT}:{OLD_SCRIPT_PATH}"],
        cwd=root,
        text=True,
    )
    old_path = Path("/tmp/materialize_0062_prereg_frozen_original.py")
    old_path.write_text(source, encoding="utf-8")

    spec = importlib.util.spec_from_file_location("m0062_frozen_original", old_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen original 0062 materializer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.ROOT = root
    module.REG = root / "config/research_registry.json"
    original_make_owner = module.make_owner

    def fixed_make_owner(registry: dict) -> dict:
        owner = original_make_owner(registry)
        owner["promotion_state"] = "NONE"
        owner["lineage_edges"] = []
        return owner

    module.make_owner = fixed_make_owner
    module.main()


if __name__ == "__main__":
    main()
