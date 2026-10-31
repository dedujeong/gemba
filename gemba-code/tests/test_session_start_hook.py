import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def session_start_commands(plugin_root):
    with open(os.path.join(plugin_root, "hooks", "hooks.json"), encoding="utf-8") as f:
        hooks = json.load(f)["hooks"]["SessionStart"]
    return [h["command"] for entry in hooks for h in entry["hooks"] if h["type"] == "command"]


def run_session_start(plugin_root, project):
    """Run every SessionStart command the way Claude Code does: in the project, with CLAUDE_PLUGIN_ROOT set."""
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=plugin_root)
    outputs = []
    for command in session_start_commands(plugin_root):
        result = subprocess.run(command, shell=True, cwd=project, env=env,
                                capture_output=True, text=True, check=True)
        outputs.append(result.stdout)
    return "".join(outputs)


def read_context(plugin_root):
    with open(os.path.join(plugin_root, "references", "context.md"), encoding="utf-8") as f:
        return f.read()


class SessionStart(unittest.TestCase):
    def setUp(self):
        self.project = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.project)

    def test_injects_the_method_rules(self):
        self.assertEqual(run_session_start(ROOT, self.project), read_context(ROOT))

    def test_uses_the_rules_of_the_installed_plugin_without_touching_the_project(self):
        plugin = os.path.join(tempfile.mkdtemp(), "gemba-code")
        self.addCleanup(shutil.rmtree, os.path.dirname(plugin))
        shutil.copytree(ROOT, plugin, ignore=shutil.ignore_patterns("evals", "tests"))
        with open(os.path.join(plugin, "references", "context.md"), "a", encoding="utf-8") as f:
            f.write("\n- A rule changed in the plugin.\n")
        self.assertIn("A rule changed in the plugin.", run_session_start(plugin, self.project))

    def test_writes_no_file_in_the_project(self):
        run_session_start(ROOT, self.project)
        self.assertEqual(os.listdir(self.project), [])


if __name__ == "__main__":
    unittest.main()
