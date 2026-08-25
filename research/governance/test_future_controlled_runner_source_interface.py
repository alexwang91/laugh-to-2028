from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"
ID_SUFFIX = re.compile(r"_(\d{4})$")
SOURCE_QUALIFIED_RUNNER = "ControlledResearchRunnerV1SourceQualified"


class FutureControlledRunnerSourceInterfaceGovernance(unittest.TestCase):
    def test_future_controlled_run_scripts_use_source_qualified_runner(self):
        """0086+ controlled run scripts may not fall back to callable-only V1.

        0085 is immutable and intentionally excluded.  This prospective guard
        applies only to future numeric research IDs.  It reads repository source
        code only and touches no controlled historical payload.
        """
        violations: list[str] = []
        for directory in sorted(RESEARCH.iterdir()):
            if not directory.is_dir():
                continue
            match = ID_SUFFIX.search(directory.name)
            if match is None or int(match.group(1)) <= 85:
                continue
            run_script = directory / "run_controlled_once.py"
            if not run_script.exists():
                continue
            text = run_script.read_text(encoding="utf-8")
            if "ControlledResearchRunnerV1" not in text:
                continue
            if SOURCE_QUALIFIED_RUNNER not in text:
                violations.append(str(run_script.relative_to(ROOT)))
        self.assertEqual(
            violations,
            [],
            "future controlled RUN must use source-qualified runner: " + ", ".join(violations),
        )


if __name__ == "__main__":
    unittest.main()
