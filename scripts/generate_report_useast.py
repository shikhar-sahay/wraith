import json
import sys
import argparse
import os
import glob
import time
import urllib.request
from datetime import datetime, timezone
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Geo lookup (ip-api.com, free, no key needed, max 45 req/min)
# ---------------------------------------------------------------------------
_geo_cache = {}

def geo_lookup(ip):
    if ip in _geo_cache:
        return _geo_cache[ip]
    try:
        url = f"http://ip-api.com/json/{ip}?fields=country,regionName,city,org,as"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        result = {
            "country": data.get("country", "Unknown"),
            "city": data.get("city", ""),
            "org": data.get("org", ""),
        }
    except Exception:
        result = {"country": "Unknown", "city": "", "org": ""}
    _geo_cache[ip] = result
    time.sleep(0.1)  # stay well under 45 req/min
    return result

# ---------------------------------------------------------------------------
# Log parsing
# ---------------------------------------------------------------------------
def parse_logs(log_path):
    events = []
    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    events.append(item)
            except json.JSONDecodeError:
                continue
    return events

def parse_multiple_logs(log_paths):
    events = []
    for path in log_paths:
        events.extend(parse_logs(path))
    return events

# ---------------------------------------------------------------------------
# Session extraction
# ---------------------------------------------------------------------------
def extract_sessions(events, excluded_ips):
    sessions = {}
    excluded_session_ids = set()

    for event in events:
        if not isinstance(event, dict):
            continue

        event_name = event.get('event')
        session_id = event.get('session_id')
        if not session_id:
            continue

        attacker_ip = event.get('attacker_ip', '') or ''
        client = event.get('client', '') or ''

        if attacker_ip in excluded_ips:
            excluded_session_ids.add(session_id)

        session = sessions.setdefault(session_id, {
            'id': session_id,
            'attacker_ip': attacker_ip,
            'client': client,
            'started_at': None,
            'ended_at': None,
            'duration_seconds': None,
            'commands_reported': None,
            'commands': [],
        })

        if attacker_ip and not session.get('attacker_ip'):
            session['attacker_ip'] = attacker_ip
        if client and not session.get('client'):
            session['client'] = client

        if event_name == 'session_started':
            session['started_at'] = event.get('timestamp')
        elif event_name == 'command_executed':
            session['commands'].append({
                'command': event.get('command', ''),
                'response': event.get('response', ''),
                'cwd': event.get('cwd', ''),
                'latency_ms': event.get('latency_ms'),
                'timestamp': event.get('timestamp'),
            })
        elif event_name == 'session_ended':
            session['ended_at'] = event.get('timestamp')
            duration_seconds = event.get('duration_seconds')
            if duration_seconds is not None:
                try:
                    session['duration_seconds'] = float(duration_seconds)
                except (TypeError, ValueError):
                    pass
            commands = event.get('commands')
            if commands is not None:
                try:
                    session['commands_reported'] = int(commands)
                except (TypeError, ValueError):
                    pass

    filtered_sessions = [s for sid, s in sessions.items() if sid not in excluded_session_ids and s.get('attacker_ip') not in excluded_ips]
    return filtered_sessions


def session_duration(session):
    duration = session.get('duration_seconds')
    if duration is not None:
        return duration
    start = session.get('started_at')
    end = session.get('ended_at')
    if not start or not end:
        return None
    try:
        s = datetime.fromisoformat(start.replace('Z', '+00:00'))
        e = datetime.fromisoformat(end.replace('Z', '+00:00'))
        return (e - s).total_seconds()
    except Exception:
        return None


def is_suspicious_command(command):
    normalized = command.strip().lower()
    suspicious_patterns = [
        'whoami', 'id', 'uname -a', 'hostname', 'ifconfig', 'ip a',
        'cat /etc/passwd', 'cat /etc/shadow', 'env', 'printenv',
        'crontab', 'authorized_keys', '.bashrc', 'wget ', 'curl ',
        'chmod ', 'chown ', 'useradd', 'history', 'find /', 'ls -la',
        'ps ', 'netstat', 'ss ', 'tar ', 'zip ', 'scp ', 'ssh ',
    ]
    return any(pattern in normalized for pattern in suspicious_patterns)

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------
def generate_report(events, date_label=None, excluded_ips=None, do_geo=True):
    excluded_ips = set(excluded_ips or [])
    sessions = extract_sessions(events, excluded_ips)

    if not date_label:
        date_label = datetime.now(timezone.utc).strftime("%d %B %Y")

    unique_ips = sorted({s.get('attacker_ip', '') for s in sessions if s.get('attacker_ip')})
    clients = Counter(s.get('client', '') for s in sessions if s.get('client'))

    total_commands = sum(len(s['commands']) for s in sessions)
    sessions_with_commands = [s for s in sessions if s['commands']]

    all_times = []
    for s in sessions:
        if s.get('started_at'):
            all_times.append(s['started_at'])
        if s.get('ended_at'):
            all_times.append(s['ended_at'])
    time_range = f"{min(all_times)} - {max(all_times)}" if all_times else "N/A"

    cmd_freq = Counter()
    suspicious_freq = Counter()
    for s in sessions:
        for c in s['commands']:
            cmd = c['command'].strip()
            if cmd:
                cmd_freq[cmd] += 1
                if is_suspicious_command(cmd):
                    suspicious_freq[cmd] += 1

    durations = [session_duration(s) for s in sessions if session_duration(s) is not None]
    avg_duration = (sum(durations) / len(durations)) if durations else None
    max_duration = max(durations) if durations else None

    # Geo lookup for all unique IPs
    geo = {}
    if do_geo:
        print(f"Looking up geo for {len(unique_ips)} IPs...", file=sys.stderr)
        for ip in unique_ips:
            if ip:
                geo[ip] = geo_lookup(ip)

    # Country stats
    countries = defaultdict(int)
    for ip in unique_ips:
        if ip and ip in geo:
            countries[geo[ip]['country']] += 1

    lines = []
    lines.append(f"# Analysis - {date_label}")
    lines.append("**Honeypot:** Wraith")
    lines.append(f"**Period:** {time_range}")
    if excluded_ips:
        lines.append("**Test traffic excluded:** Yes")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Unique attacker IPs | {len(unique_ips)} |")
    lines.append(f"| Total sessions | {len(sessions)} |")
    lines.append(f"| Sessions with commands | {len(sessions_with_commands)} |")
    lines.append(f"| Total commands executed | {total_commands} |")
    lines.append(f"| Unique clients | {len(clients)} |")
    if avg_duration is not None:
        lines.append(f"| Avg session duration | {avg_duration:.2f} s |")
        lines.append(f"| Longest session | {max_duration:.2f} s |")
    if countries:
        lines.append(f"| Countries observed | {', '.join(sorted(countries.keys()))} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Attacking IPs")
    lines.append("")
    if do_geo:
        lines.append("| IP | Country | Organization | Sessions | Commands | Clients |")
        lines.append("|----|---------|--------------|----------|----------|---------|")
    else:
        lines.append("| IP | Sessions | Commands | Clients |")
        lines.append("|----|----------|----------|---------|")

    ip_sessions = defaultdict(list)
    for s in sessions:
        ip_sessions[s.get('attacker_ip', '')].append(s)

    for ip, sess in sorted(ip_sessions.items()):
        cmds = sum(len(s['commands']) for s in sess)
        client_names = sorted({s.get('client', '') for s in sess if s.get('client')})
        client = ', '.join(client_names) if client_names else 'N/A'
        if do_geo and ip in geo:
            g = geo[ip]
            country = g['country']
            org = g['org'][:40] if g['org'] else 'Unknown'
            lines.append(f"| {ip} | {country} | {org} | {len(sess)} | {cmds} | {client} |")
        else:
            lines.append(f"| {ip} | {len(sess)} | {cmds} | {client} |")
    lines.append("")

    if cmd_freq:
        lines.append("---")
        lines.append("")
        lines.append("## Commands Executed")
        lines.append("")
        lines.append("| Command | Count |")
        lines.append("|---------|-------|")
        for cmd, count in sorted(cmd_freq.items(), key=lambda x: -x[1]):
            lines.append(f"| {cmd} | {count} |")
        lines.append("")

    if suspicious_freq:
        lines.append("---")
        lines.append("")
        lines.append("## Suspicious Commands")
        lines.append("")
        lines.append("| Command | Count |")
        lines.append("|---------|-------|")
        for cmd, count in sorted(suspicious_freq.items(), key=lambda x: -x[1]):
            lines.append(f"| {cmd} | {count} |")
        lines.append("")

    if sessions_with_commands:
        lines.append("---")
        lines.append("")
        lines.append("## Session Details - Attacker Activity Inside Honeypot")
        lines.append("")
        lines.append("*These are sessions where an attacker successfully logged in and ran commands.*")
        lines.append("")
        for s in sessions_with_commands:
            dur = session_duration(s)
            dur_str = f"{dur:.0f}s" if dur else "N/A"
            ip = s['attacker_ip']
            geo_str = ""
            if do_geo and ip in geo:
                g = geo[ip]
                geo_str = f" - {g['country']}, {g['org']}"
            client = s.get('client') or 'N/A'
            lines.append(f"### Session {s['id'][:8]} - {ip}{geo_str} ({dur_str})")
            lines.append("")
            lines.append(f"**Client:** {client}")
            lines.append(f"**Commands reported:** {s['commands_reported'] if s.get('commands_reported') is not None else len(s['commands'])}")
            lines.append("")
            lines.append("| # | Command | Response | CWD | Latency ms |")
            lines.append("|---|---------|----------|-----|------------|")
            for i, c in enumerate(s['commands'], 1):
                cmd = c['command'].replace('|', '\\|')
                out = (c['response'] or '').replace('\n', ' ').replace('|', '\\|')[:100]
                cwd = (c.get('cwd') or '').replace('|', '\\|')
                latency = c.get('latency_ms')
                latency_str = f"{latency:.3f}" if isinstance(latency, (int, float)) else "N/A"
                lines.append(f"| {i} | {cmd} | {out} | {cwd} | {latency_str} |")
            lines.append("")
            # Command intent summary
            lines.append("**Command sequence analysis:**")
            cmds = [c['command'] for c in s['commands'] if c['command']]
            recon = [c for c in cmds if c in ['whoami','id','uname -a','hostname','ifconfig','ip a','cat /etc/passwd','cat /etc/shadow','env','printenv']]
            persistence = [c for c in cmds if any(k in c for k in ['crontab','authorized_keys','.bashrc','wget','curl','chmod','useradd'])]
            exfil = [c for c in cmds if any(k in c for k in ['cat /etc','history','find /','ls -la'])]
            if recon:
                lines.append(f"- **Reconnaissance:** {', '.join(f'{c}' for c in recon)}")
            if persistence:
                lines.append(f"- **Persistence attempts:** {', '.join(f'{c}' for c in persistence)}")
            if exfil:
                lines.append(f"- **Enumeration:** {', '.join(f'{c}' for c in exfil)}")
            if not recon and not persistence and not exfil:
                lines.append("- No clearly categorized activity detected")
            lines.append("")
    else:
        lines.append("---")
        lines.append("")
        lines.append("## Session Details - Attacker Activity Inside Honeypot")
        lines.append("")
        lines.append("*No successful logins with command execution yet. Attackers are currently in the brute-force phase.*")
        lines.append("")

    if clients:
        lines.append("---")
        lines.append("")
        lines.append("## Clients Used")
        lines.append("")
        lines.append("| Client | Count | Notes |")
        lines.append("|--------|-------|-------|")
        known = {
            "SSH-2.0-libssh_0.7.4": "Known attack tool (libssh scanner)",
            "SSH-2.0-Go": "Go-based mass scanner",
            "MGLNDD": "Honeypot fingerprinter",
            "SSH-2.0-OpenSSH_for_Windows": "Windows OpenSSH client",
        }
        for client, count in sorted(clients.items(), key=lambda x: -x[1]):
            note = next((v for k, v in known.items() if k in client), "")
            lines.append(f"| {client} | {count} | {note} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Research Notes")
    lines.append("")
    lines.append("*(Add manual observations here after reviewing the session details above)*")
    lines.append("")

    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Wraith honeypot report")
    parser.add_argument("log_path", nargs="?", default="/home/ubuntu/beelzebub/logs")
    parser.add_argument("date_label", nargs="?", default=None)
    parser.add_argument("--exclude-ip", action="append", default=[],
                        help="IP to exclude (repeatable)")
    parser.add_argument("--out-dir", default=None,
                        help="Write report to this directory instead of stdout")
    parser.add_argument("--all", action="store_true",
                        help="Combine ALL log files into one cumulative report")
    parser.add_argument("--out-file", default=None,
                        help="Custom output filename")
    parser.add_argument("--no-geo", action="store_true",
                        help="Skip geo lookup (faster, offline)")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(args.log_path))
    do_geo = not args.no_geo

    if args.all:
        pattern = os.path.join(base_dir, "logs*")
        all_files = sorted(f for f in glob.glob(pattern) if os.path.isfile(f))
        if not all_files:
            print("No log files found.", file=sys.stderr)
            sys.exit(1)
        print(f"Combining {len(all_files)} log files: {[os.path.basename(f) for f in all_files]}", file=sys.stderr)
        events = parse_multiple_logs(all_files)
        date_label = args.date_label or "Cumulative - All Time"
    else:
        events = parse_logs(args.log_path)
        date_label = args.date_label

    report = generate_report(events, date_label, excluded_ips=args.exclude_ip, do_geo=do_geo)

    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        if args.out_file:
            fname = args.out_file
        elif args.all:
            fname = "cumulative.md"
        else:
            fname = datetime.now(timezone.utc).strftime("%Y-%m-%d") + ".md"
        fpath = os.path.join(args.out_dir, fname)
        with open(fpath, "w") as f:
            f.write(report)
        print(f"Report written to {fpath}")
    else:
        print(report)
