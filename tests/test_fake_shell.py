import json
import tempfile
import threading
import time
import unittest
import urllib.request

from wraith.server import FakeShellServer, start_http_server


class FakeShellTests(unittest.TestCase):
    def test_session_starts_with_fake_linux_context(self) -> None:
        server = FakeShellServer()
        session = server.create_session("1.2.3.4", "SSH-2.0-OpenSSH_8.9")

        self.assertEqual(session.user, "admin")
        self.assertEqual(session.hostname, "db-prod-01")
        self.assertEqual(session.cwd, "/home/admin")

    def test_basic_commands_change_state_and_return_output(self) -> None:
        server = FakeShellServer()
        session = server.create_session("1.2.3.4", "SSH-2.0-OpenSSH_8.9")

        pwd_output = session.handle_command("pwd")
        self.assertTrue(pwd_output.strip().endswith("/home/admin"))

        mkdir_output = session.handle_command("mkdir /tmp/demo")
        self.assertTrue("created" in mkdir_output.lower() or "mkdir" in mkdir_output.lower())

        ls_output = session.handle_command("ls /tmp")
        self.assertIn("demo", ls_output)

    def test_sudo_escalation_is_simulated(self) -> None:
        server = FakeShellServer()
        session = server.create_session("1.2.3.4", "SSH-2.0-OpenSSH_8.9")

        first = session.handle_command("sudo whoami")
        self.assertTrue("password" in first.lower() or "sudo" in first.lower())

        second = session.handle_command("sudo whoami")
        self.assertTrue("root" in second.lower() or "permission" in second.lower() or "try again" in second.lower())

    def test_http_endpoint_returns_command_output(self) -> None:
        temp_dir = tempfile.mkdtemp(prefix="wraith-test-", dir=tempfile.gettempdir())
        thread = threading.Thread(
            target=start_http_server,
            kwargs={"host": "127.0.0.1", "port": 8767, "telemetry_dir": temp_dir},
            daemon=True,
        )
        thread.start()
        time.sleep(0.5)

        first_payload = json.dumps({"attacker_ip": "1.2.3.4", "client": "SSH", "command": "mkdir /tmp/deploy-test"}).encode("utf-8")
        first_request = urllib.request.Request(
            "http://127.0.0.1:8767/command",
            data=first_payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(first_request, timeout=3) as response:
            first_body = json.loads(response.read().decode("utf-8"))

        second_payload = json.dumps({"attacker_ip": "1.2.3.4", "client": "SSH", "command": "ls /tmp"}).encode("utf-8")
        second_request = urllib.request.Request(
            "http://127.0.0.1:8767/command",
            data=second_payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(second_request, timeout=3) as response:
            second_body = json.loads(response.read().decode("utf-8"))

        self.assertIn("created directory", first_body["output"].lower())
        self.assertIn("deploy-test", second_body["output"])


if __name__ == "__main__":
    unittest.main()
