import unittest

from research.governance import test_brrk_exhaustion_pulse_0046_closeout as closeout


class TestBrrkExhaustionPulse0046CloseoutBridge(unittest.TestCase):
    def test_all_closeout_contract_functions(self):
        names = [
            name
            for name in sorted(dir(closeout))
            if name.startswith("test_") and callable(getattr(closeout, name))
        ]
        self.assertTrue(names, "no 0046 closeout contract functions discovered")
        for name in names:
            with self.subTest(contract=name):
                getattr(closeout, name)()


if __name__ == "__main__":
    unittest.main()
