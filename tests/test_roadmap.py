import contextlib
import io
import tempfile
import textwrap
import unittest
from pathlib import Path

import roadmap

README = "# Title\n\n<!-- roadmap:start -->\nstale\n<!-- roadmap:end -->\n\nFooter\n"

VALID = """
[roadmaps]
python = "https://roadmap.sh/python"

[[nodes]]
roadmap = "python"
node = "uv"
title = "uv"
status = "evidenced"
evidence = ["skeletons/python-api"]

[[nodes]]
roadmap = "python"
node = "pytest"
title = "pytest"
status = "pending"
evidence = []
"""


class RepoTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "skeletons" / "python-api").mkdir(parents=True)
        (self.root / "README.md").write_text(README, encoding="utf-8")

    def write_roadmap(self, content: str) -> None:
        (self.root / "roadmap.toml").write_text(textwrap.dedent(content), encoding="utf-8")

    def run_cli(self, command: str) -> tuple[int, str]:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            code = roadmap.main([command, "--root", str(self.root)])
        return code, stderr.getvalue()

    def assert_problem(self, content: str, fragment: str) -> None:
        self.write_roadmap(content)
        with self.assertRaises(roadmap.RoadmapError) as ctx:
            roadmap.load(self.root)
        self.assertTrue(
            any(fragment in p for p in ctx.exception.problems),
            f"expected '{fragment}' in {ctx.exception.problems}",
        )


class LoadTest(RepoTestCase):
    def test_valid_file_loads_in_order(self) -> None:
        self.write_roadmap(VALID)
        loaded = roadmap.load(self.root)
        self.assertEqual([n.node for n in loaded.nodes], ["uv", "pytest"])
        self.assertIs(loaded.nodes[0].status, roadmap.Status.EVIDENCED)

    def test_evidenced_without_evidence_fails(self) -> None:
        self.assert_problem(
            VALID.replace('["skeletons/python-api"]', "[]"), "needs at least one evidence"
        )

    def test_pending_with_evidence_fails(self) -> None:
        self.assert_problem(
            VALID.replace('status = "evidenced"', 'status = "pending"'), "lists evidence"
        )

    def test_missing_evidence_path_fails(self) -> None:
        self.assert_problem(VALID.replace("python-api", "nope"), "does not exist")

    def test_evidence_outside_repo_fails(self) -> None:
        self.assert_problem(VALID.replace("skeletons/python-api", "../x"), "inside the repo")

    def test_unknown_roadmap_fails(self) -> None:
        self.assert_problem(
            VALID.replace('roadmap = "python"', 'roadmap = "rust"', 1), "not declared"
        )

    def test_unknown_status_fails(self) -> None:
        self.assert_problem(VALID.replace('"evidenced"', '"done"'), "status must be one of")

    def test_duplicate_node_fails(self) -> None:
        self.assert_problem(VALID.replace('node = "pytest"', 'node = "uv"'), "duplicate node")

    def test_unknown_key_fails(self) -> None:
        self.assert_problem(
            VALID.replace('title = "uv"', 'title = "uv"\nlevel = 3'), "unknown keys"
        )

    def test_non_roadmap_url_fails(self) -> None:
        self.assert_problem(
            VALID.replace("https://roadmap.sh/python", "https://x.dev"), "must start"
        )


class CliTest(RepoTestCase):
    def test_check_fails_when_readme_is_stale(self) -> None:
        self.write_roadmap(VALID)
        code, stderr = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("make readme", stderr)

    def test_render_then_check_passes(self) -> None:
        self.write_roadmap(VALID)
        self.assertEqual(self.run_cli("render")[0], 0)
        self.assertEqual(self.run_cli("check"), (0, ""))

        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("Evidenced: **1 / 2**", readme)
        self.assertIn("[`skeletons/python-api`](skeletons/python-api)", readme)
        self.assertNotIn("stale", readme)
        self.assertTrue(readme.endswith("<!-- roadmap:end -->\n\nFooter\n"))

    def test_missing_markers_fails(self) -> None:
        self.write_roadmap(VALID)
        (self.root / "README.md").write_text("# No markers\n", encoding="utf-8")
        code, stderr = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("roadmap:start", stderr)


if __name__ == "__main__":
    unittest.main()
