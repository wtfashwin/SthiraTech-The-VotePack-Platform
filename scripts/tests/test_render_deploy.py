"""Exercise the deployment guard without contacting a provider."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "request_render_deploy.sh"


class RenderDeployTests(unittest.TestCase):
    def run_script(self, hook, status="200", curl_exit="0"):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            marker = temp / "curl-called"
            curl = temp / "curl"
            curl.write_text(
                '#!/bin/sh\nprintf called > "$CURL_MARKER"\n'
                'printf "%s" "$CURL_STATUS"\nexit "$CURL_EXIT"\n'
            )
            curl.chmod(0o755)
            env = os.environ.copy()
            env.update(
                PATH=f"{temp}:{env['PATH']}",
                CURL_MARKER=str(marker),
                CURL_STATUS=status,
                CURL_EXIT=curl_exit,
            )
            env.pop("RENDER_DEPLOY_HOOK_URL", None)
            if hook is not None:
                env["RENDER_DEPLOY_HOOK_URL"] = hook
            result = subprocess.run(
                ["bash", str(SCRIPT)], capture_output=True, text=True, env=env
            )
            return result, marker.exists()

    def test_unconfigured_hook_fails_without_request(self):
        for hook in (None, "", " \t\n"):
            with self.subTest(hook=hook):
                result, requested = self.run_script(hook)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("RENDER_DEPLOY_HOOK_URL", result.stderr)
                self.assertFalse(requested)

    def test_malformed_hook_fails_without_request(self):
        for hook in (
            "http://api.render.com/deploy/srv-example?key=test",
            "https://example.invalid/deploy/srv-example?key=test",
            "https://api.render.com/deploy/srv-example?key=test\n",
        ):
            with self.subTest(hook=hook):
                result, requested = self.run_script(hook)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(requested)

    def test_http_request_failure_propagates(self):
        result, requested = self.run_script(
            "https://api.render.com/deploy/srv-example?key=test", "401", "22"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(requested)
        self.assertNotIn("accepted", result.stdout)

    def test_accepted_response_does_not_claim_deployed(self):
        for status in ("200", "202"):
            with self.subTest(status=status):
                result, requested = self.run_script(
                    "https://api.render.com/deploy/srv-example?key=test", status
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(requested)
                self.assertIn("accepted", result.stdout)
                self.assertNotIn("Deployment completed", result.stdout)
                self.assertNotIn("key=test", result.stdout + result.stderr)

    def test_unexpected_success_code_fails(self):
        result, requested = self.run_script(
            "https://api.render.com/deploy/srv-example?key=test", "302"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(requested)


if __name__ == "__main__":
    unittest.main()
