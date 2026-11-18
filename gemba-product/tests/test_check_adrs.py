import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "architecture", "scripts", "check_adrs.py")


def adr(adr_id, state="Accepted", spike=None, superseded_by=None):
    return {"id": adr_id, "state": state, "spike": spike, "superseded_by": superseded_by}


def check(adrs, architecture=None, spikes=None):
    """Run the script over a space: the ADRs, the state the Architecture page shows for each, and the Spikes."""
    if architecture is None:
        architecture = {a["id"]: a["state"] for a in adrs}
    space = {"adrs": adrs, "architecture": architecture, "spikes": spikes or {}}
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "space.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(space, f)
        result = subprocess.run([sys.executable, SCRIPT, path], capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class AcceptedAdrWithAnOpenSpike(unittest.TestCase):
    def test_an_accepted_adr_whose_spike_is_not_done_is_a_discordance(self):
        code, out, _ = check([adr("ADR-0001", spike="GEMBA-12")], spikes={"GEMBA-12": "Implement"})
        self.assertEqual(code, 1)
        self.assertIn("ADR-0001", out)
        self.assertIn("GEMBA-12", out)
        self.assertIn("Implement", out)

    def test_an_accepted_adr_whose_spike_is_done_is_not(self):
        code, out, _ = check([adr("ADR-0001", spike="GEMBA-12")], spikes={"GEMBA-12": "Done"})
        self.assertEqual((code, out), (0, ""))

    def test_a_spike_the_input_does_not_have_cannot_be_confirmed_done(self):
        code, out, _ = check([adr("ADR-0001", spike="GEMBA-99")], spikes={"GEMBA-12": "Done"})
        self.assertEqual(code, 1)
        self.assertIn("GEMBA-99", out)

    def test_an_adr_still_waiting_on_its_spike_is_not_a_discordance(self):
        code, out, _ = check([adr("ADR-0001", state="Waiting on a Spike", spike="GEMBA-12")], spikes={"GEMBA-12": "Implement"})
        self.assertEqual((code, out), (0, ""))


class StateOnTheArchitecturePage(unittest.TestCase):
    def test_an_adr_shown_with_another_state_on_the_page_is_a_discordance(self):
        code, out, _ = check([adr("ADR-0001")], architecture={"ADR-0001": "Ready to decide"})
        self.assertEqual(code, 1)
        self.assertIn("ADR-0001", out)
        self.assertIn("Ready to decide", out)
        self.assertIn("Accepted", out)

    def test_an_adr_shown_with_its_own_state_is_not(self):
        code, out, _ = check([adr("ADR-0001", state="Ready to decide")], architecture={"ADR-0001": "Ready to decide"})
        self.assertEqual((code, out), (0, ""))

    def test_each_adr_is_compared_with_its_own_line_of_the_page(self):
        code, out, _ = check([adr("ADR-0001"), adr("ADR-0002", state="Proposed")],
                             architecture={"ADR-0001": "Accepted", "ADR-0002": "Accepted"})
        self.assertEqual(code, 1)
        self.assertEqual(out.count("\n"), 1)
        self.assertIn("ADR-0002", out)


if __name__ == "__main__":
    unittest.main()
