from wraith.server import FakeShellServer


if __name__ == "__main__":
    server = FakeShellServer(telemetry_dir="logs/telemetry")
    session = server.create_session("203.0.113.10", "OpenSSH_9.0")
    print(session.banner())
    print(session.prompt())
    for command in ["pwd", "whoami", "uname -a", "mkdir /tmp/demo", "ls /tmp", "sudo whoami"]:
        print(f"$ {command}")
        print(session.handle_command(command))
        print(session.prompt())
