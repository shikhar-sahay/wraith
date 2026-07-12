from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any

from .filesystem import FakeFilesystem
from .input_layer import InputLayer
from .network_backend import NetworkBackend
from .parser import CommandParser
from .persona import MachinePersona
from .privesc import PrivilegeEscalationSimulator
from .randomizer import SessionRandomizer
from .registry import Registry
from .session_identity import SessionIdentity
from .telemetry import TelemetryLogger


class FakeShellServer:
    def __init__(self, telemetry_dir: str | None = None) -> None:
        self.telemetry = TelemetryLogger(telemetry_dir)
        self.registry = Registry()
        self.persona = MachinePersona()

    def create_session(self, attacker_ip: str, client: str) -> "FakeShellSession":
        session_id = hashlib.sha256(f"{attacker_ip}:{client}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]
        session = FakeShellSession(
            session_id=session_id,
            attacker_ip=attacker_ip,
            client=client,
            server=self,
        )
        self.telemetry.log_event(
            {
                "event": "session_started",
                "session_id": session.session_id,
                "attacker_ip": attacker_ip,
                "client": client,
            }
        )
        return session


class FakeShellSession:
    def __init__(self, session_id: str, attacker_ip: str, client: str, server: FakeShellServer) -> None:
        self.session_id = session_id
        self.attacker_ip = attacker_ip
        self.client = client
        self.server = server
        self.started_monotonic = time.perf_counter()
        self.identity = SessionIdentity(
            session_id=session_id,
            attacker_ip=attacker_ip,
            client=client,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self.filesystem = FakeFilesystem()
        self.randomizer = SessionRandomizer(seed=abs(hash(session_id)))
        self.registry = server.registry
        self.command_count = 0
        self.network = NetworkBackend()
        self.input_layer = InputLayer()
        self.persona = server.persona
        self.privesc = PrivilegeEscalationSimulator()

    @property
    def user(self) -> str:
        return self.identity.user

    @property
    def hostname(self) -> str:
        return self.identity.hostname

    @property
    def cwd(self) -> str:
        return self.identity.cwd

    def banner(self) -> str:
        return self.persona.banner()

    def prompt(self) -> str:
        return self.input_layer.render_prompt(self.identity.user, self.identity.hostname, self.identity.cwd)

    def handle_command(self, raw: str) -> str:
        command_started = time.perf_counter()
        self.command_count += 1
        parsed = CommandParser.parse(raw)
        self.identity.history.append(raw)
        if parsed.command in {"", None}:
            return ""

        command = parsed.command
        args = parsed.args

        if command == "pwd":
            output = self.identity.cwd
        elif command == "whoami":
            output = self.identity.user
        elif command == "id":
            output = f"uid=1000(admin) gid=1000(admin) groups=1000(admin)"
        elif command == "hostname":
            output = self.identity.hostname
        elif command == "hostnamectl":
            output = "Static hostname: db-prod-01\nIcon name: computer-server\nChassis: server"
        elif command == "uname":
            output = "Linux db-prod-01 5.15.0-105-generic #115-Ubuntu SMP Tue Jun 4 11:00:00 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux"
        elif command == "uname" and args and args[0] == "-a":
            output = "Linux db-prod-01 5.15.0-105-generic #115-Ubuntu SMP Tue Jun 4 11:00:00 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux"
        elif command == "lscpu":
            output = "Architecture: x86_64\nCPU(s): 16\nModel name: Intel Xeon"
        elif command == "free":
            output = "              total        used        free      shared  buff/cache   available\nMem:          65536        12000       43000         100       10536       50000"
        elif command == "df":
            output = "Filesystem     Size  Used Avail Use% Mounted on\n/dev/sda1       500G  120G  360G  25% /"
        elif command == "ps":
            output = "PID TTY TIME CMD\n123 sshd: admin [priv]\n456 python3 /opt/agent.py"
        elif command == "top":
            output = "top - 12:34:56 up 3 days,  1:02,  2 users,  load average: 0.12, 0.08, 0.03"
        elif command == "env" or command == "printenv":
            output = "HOSTNAME=db-prod-01\nUSER=admin\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        elif command == "history":
            output = "\n".join(self.identity.history[-8:])
        elif command == "cd":
            target = args[0] if args else "/home/admin"
            if target in {"~", "~/"}:
                target = "/home/admin"
            if target.startswith("~"):
                target = "/home/admin" + target[1:]
            if target in {"/", "/home", "/home/admin", "/tmp", "/var/www", "/root"} or self.filesystem.exists(target):
                self.identity.cwd = target
                output = ""
            else:
                output = f"bash: cd: {target}: No such file or directory"
        elif command == "mkdir":
            target = args[0] if args else "/tmp"
            output = self.filesystem.mkdir(target)
            if not output:
                output = f"mkdir: created directory '{target}'"
        elif command == "ls":
            target = args[0] if args else self.identity.cwd
            output = self.filesystem.ls(target)
        elif command == "cat":
            target = args[0] if args else "/etc/hostname"
            content = self.filesystem.cat(target)
            output = content if content is not None else f"cat: {target}: No such file or directory"
        elif command == "touch":
            target = args[0] if args else "/tmp/file"
            self.filesystem.touch(target)
            output = ""
        elif command == "rm":
            target = args[0] if args else "/tmp/file"
            output = self.filesystem.remove(target)
        elif command == "cp":
            src, dst = args[0], args[1] if len(args) > 1 else "/tmp/copy"
            content = self.filesystem.cat(src)
            if content is None:
                output = f"cp: cannot stat '{src}': No such file or directory"
            else:
                self.filesystem.write(dst, content)
                output = ""
        elif command == "mv":
            src, dst = args[0], args[1] if len(args) > 1 else "/tmp/moved"
            content = self.filesystem.cat(src)
            if content is None:
                output = f"mv: cannot stat '{src}': No such file or directory"
            else:
                self.filesystem.write(dst, content)
                self.filesystem.remove(src)
                output = ""
        elif command == "head" or command == "tail":
            target = args[0] if args else "/etc/hostname"
            content = self.filesystem.cat(target)
            output = content if content is not None else f"{command}: {target}: No such file or directory"
        elif command == "find":
            output = "/home/admin\n/tmp\n/var/www\n"
        elif command == "grep":
            output = "No matches found"
        elif command == "ip" and args and args[0] == "a":
            output = "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000\n2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000"
        elif command == "ifconfig":
            output = "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n        inet 10.0.0.5  netmask 255.255.255.0"
        elif command == "ss":
            output = "State Recv-Q Send-Q Local Address:Port Peer Address:Port\nESTAB 0 0 10.0.0.5:22 203.0.113.12:51234"
        elif command == "netstat":
            output = "Active Internet connections (servers and established)\nProto Recv-Q Send-Q Local Address Foreign Address State"
        elif command == "systemctl":
            output = "System has not been booted with systemd as init system (PID 1). Can't operate."
        elif command == "service":
            output = "[ ok ] mysql: started"
        elif command == "crontab":
            output = "no crontab for admin"
        elif command == "chmod":
            output = ""
        elif command == "chown":
            output = ""
        elif command == "tar":
            output = "tar: Removing leading `/' from member names"
        elif command == "gzip":
            output = ""
        elif command == "zip":
            output = "adding: /tmp/archive/"
        elif command == "scp":
            output = "[fake] scp request logged"
            self.registry.record_reverse_shell(raw)
        elif command == "ssh":
            output = "[fake] ssh request logged"
            self.registry.record_reverse_shell(raw)
        elif command == "wget" or command == "curl":
            url = args[0] if args else "http://example.com"
            filename = "/tmp/" + self.randomizer.choice(["payload", "script", "package", "agent"]) + ".sh"
            self.filesystem.write(filename, f"# downloaded from {url}\n")
            self.registry.record_download(url, filename)
            output = f"[fake download] downloaded {url} to {filename}"
        elif command == "python3":
            output = "Python 3.10.12 (main, Jun 4 2024, 19:00:00)\n[GCC 11.4.0] on linux"
        elif command == "bash":
            output = "GNU bash, version 5.1.16(1)-release (x86_64-pc-linux-gnu)"
        elif command == "perl":
            output = "This is perl 5.34.0, threaded x86_64-linux-gnu"
        elif command == "echo":
            output = " ".join(args)
        elif command == "export":
            if args:
                key, _, value = args[0].partition("=")
                self.identity.environment[key] = value
            output = ""
        elif command == "alias":
            output = "alias ll='ls -al'"
        elif command == "clear":
            output = "\033c"
        elif command == "exit":
            output = "logout"
        elif command == "sudo":
            output = self.privesc.next(self.identity.user)
            if output == "root@db-prod-01:~#":
                self.identity.root_mode = True
        elif command == "su":
            if self.identity.root_mode:
                output = "root@db-prod-01:~#"
            else:
                self.identity.sudo_attempts += 1
                output = "su: Authentication failure"
                if self.identity.sudo_attempts >= 2:
                    self.identity.root_mode = True
                    output = "root@db-prod-01:~#"
        else:
            output = f"bash: {command}: command not found"

        latency_ms = (time.perf_counter() - command_started) * 1000.0

        self.server.telemetry.log_event(
            {
                "event": "command_executed",
                "session_id": self.session_id,
                "attacker_ip": self.attacker_ip,
                "client": self.client,
                "command": raw,
                "response": output,
                "cwd": self.identity.cwd,
                "latency_ms": latency_ms,
            }
        )

        if command == "exit":
            self.server.telemetry.log_session_ended(
                session_id=self.session_id,
                attacker_ip=self.attacker_ip,
                client=self.client,
                duration_seconds=time.perf_counter() - self.started_monotonic,
                commands=self.command_count,
            )

        return output


def start_http_server(host: str = "127.0.0.1", port: int = 8765, telemetry_dir: str | None = None) -> None:
    server = FakeShellServer(telemetry_dir=telemetry_dir)
    sessions: dict[tuple[str, str], FakeShellSession] = {}

    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/command":
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body or "{}")
            attacker_ip = payload.get("attacker_ip", "unknown")
            client = payload.get("client", "unknown")
            command = payload.get("command", "")
            session_key = (attacker_ip, client)
            if session_key not in sessions:
                sessions[session_key] = server.create_session(attacker_ip, client)
            session = sessions[session_key]
            output = session.handle_command(command)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"output": output}).encode("utf-8"))

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    httpd = HTTPServer((host, port), RequestHandler)
    httpd.serve_forever()
