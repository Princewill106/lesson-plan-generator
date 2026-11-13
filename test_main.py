import json
import unittest

import main


class PlanTests(unittest.TestCase):
    def test_timings_add_up(self):
        for m in (35, 40, 45, 80):
            self.assertEqual(sum(t for _, t in main.timings(m)), m)

    def test_plan_has_parts(self):
        p = main.plan(json.load(open("sample_scheme.json"))[0])
        self.assertEqual(len(p["objectives"]), 3)
        self.assertEqual(len(p["phases"]), 5)
        self.assertIn("## Exit ticket", main.to_md(p))


if __name__ == "__main__":
    unittest.main()
