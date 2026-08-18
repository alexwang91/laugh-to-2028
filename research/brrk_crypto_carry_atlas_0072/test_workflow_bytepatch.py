from __future__ import annotations

import unittest
from pathlib import Path

from research.brrk_crypto_carry_atlas_0072.workflow_bytepatch import JOB_INSERTION, TEST_INSERTION, patch_bytes


class WorkflowBytePatchTests(unittest.TestCase):
    def test_actual_workflow_patch_is_additive_and_reversible(self) -> None:
        root = Path(__file__).resolve().parents[2]
        original = (root / '.github/workflows/research-governance.yml').read_bytes()
        result = patch_bytes(original)
        self.assertEqual(result.original, original)
        text = result.patched.decode('utf-8')
        self.assertEqual(text.count(TEST_INSERTION), 1)
        self.assertEqual(text.count('carry-atlas-0072-first-capture-execution:'), 1)
        self.assertIn(JOB_INSERTION.strip(), text)
        self.assertNotIn('[0072_FIRST_CAPTURE_EXECUTE_V1]', original.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
