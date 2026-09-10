import json
import sys
import argparse
import os
import glob
import time
import urllib.request
from datetime import datetime, timezone
from collections import defaultdict

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
                events.append(json.loads(line))
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
    login_attempts = []

    for e in events:
        if 'event' not in e:
            continue
        ev = e['event']
        status = ev.get('Status', '')
        sid = ev.get('ID', '')
        ip = ev.get('SourceIp')

        if ip in excluded_ips:
            continue

        if status == 'Stateless':
            login_attempts.append(ev)

        elif status == 'Start':
            sessions[sid] = {
                'id': sid,
                'start': ev.get('DateTime'),
                'ip': ip,
                'port': ev.get('SourcePort'),
                'user': ev.get('User', ''),
                'client': ev.get('Client', ''),
                'protocol': ev.get('Protocol', ''),
                'commands': []
            }

        elif status == 'Interaction':
            if sid in sessions:
                sessions[sid]['commands'].append({
                    'command': ev.get('Command', ''),
                    'output': ev.get('CommandOutput', ''),
                    'time': ev.get('DateTime')
                })
                sessions[sid]['end'] = ev.get('DateTime')

    return list(sessions.values()), login_attempts

def extract_llm_stats(events):
    stats = []
    for e in events:
        msg = e.get('msg', '')
        if 'total_duration' in msg:
            try:
                data = json.loads(msg)
                stats.append({
                    'model': data.get('model'),
                    'total_duration_ms': data.get('total_duration', 0) / 1_000_000,
                    'eval_count': data.get('eval_count', 0),
                    'prompt_eval_count': data.get('prompt_eval_count', 0),
                })
            except Exception:
                pass
    return stats

def session_duration(session):
    start = session.get('start')
    end = session.get('end')
    if not start or not end:
        return None
    try:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        s = datetime.strptime(start, fmt)
        e = datetime.strptime(end, fmt)
        return (e - s).total_seconds()
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------
def generate_report(events, date_label=None, excluded_ips=None, do_geo=True):
    excluded_ips = set(excluded_ips or [])
    sessions, login_attempts = extract_sessions(events, excluded_ips)
    login_attempts = [a for a in login_attempts if a.get('SourceIp') not in excluded_ips]
    llm_stats = extract_llm_stats(events)

    if not date_label:
        date_label = datetime.now(timezone.utc).strftime("%d %B %Y")

    unique_ips = set(s['ip'] for s in sessions if s['ip'])
    login_ips = set(a.get('SourceIp') for a in login_attempts)
    all_ips = unique_ips | login_ips

    total_commands = sum(len(s['commands']) for s in sessions)
    sessions_with_commands = [s for s in sessions if s['commands']]

    all_times = []
    for e in events:
        if 'event' in e:
            ev = e['event']
            if ev.get('SourceIp') in excluded_ips:
                continue
            dt = ev.get('DateTime')
            if dt:
                all_times.append(dt)
    time_range = f"{min(all_times)} - {max(all_times)}" if all_times else "N/A"

    if llm_stats:
        avg_latency = sum(s['total_duration_ms'] for s in llm_stats) / len(llm_stats)
        avg_tokens = sum(s['eval_count'] for s in llm_stats) / len(llm_stats)
    else:
        avg_latency = 0
        avg_tokens = 0

    passwords = defaultdict(int)
    for a in login_attempts:
        pw = a.get('Password', '')
        if pw:
            passwords[pw] += 1

    clients = defaultdict(int)
    for a in login_attempts:
        c = a.get('Client', '')
        if c:
            clients[c] += 1

    cmd_freq = defaultdict(int)
    for s in sessions:
        for c in s['commands']:
            cmd = c['command'].strip()
            if cmd:
                cmd_freq[cmd] += 1

    # Geo lookup for all unique IPs
    geo = {}
    if do_geo:
        print(f"Looking up geo for {len(all_ips)} IPs...", file=sys.stderr)
        for ip in all_ips:
            if ip:
                geo[ip] = geo_lookup(ip)

    # Country stats
    countries = defaultdict(int)
    for ip in all_ips:
        if ip and ip in geo:
            countries[geo[ip]['country']] += 1

    lines = []
    lines.append(f"# Analysis - {date_label}")
    lines.append(f"**Honeypot:** Wraith (Beelzebub + qwen2.5:0.5b via Ollama)")
    lines.append("**Region:** Mumbai (ap-south-1)")
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
    lines.append(f"| Unique IPs | {len(all_ips)} |")
    lines.append(f"| Total sessions | {len(sessions)} |")
    lines.append(f"| Login attempts | {len(login_attempts)} |")
    lines.append(f"| Sessions with commands | {len(sessions_with_commands)} |")
    lines.append(f"| Total commands executed | {total_commands} |")
    lines.append(f"| Avg LLM response latency | {avg_latency:.0f} ms |")
    lines.append(f"| Avg tokens generated | {avg_tokens:.1f} |")
    if countries:
        lines.append(f"| Countries observed | {', '.join(sorted(countries.keys()))} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Attacking IPs")
    lines.append("")
    if do_geo:
        lines.append("| IP | Country | Organization | Sessions | Commands | SSH Client |")
        lines.append("|----|---------|--------------|----------|----------|------------|")
    else:
        lines.append("| IP | Sessions | Commands | SSH Client |")
        lines.append("|----|----------|----------|------------|")

    ip_sessions = defaultdict(list)
    for s in sessions:
        ip_sessions[s['ip']].append(s)
    for a in login_attempts:
        ip = a.get('SourceIp')
        if ip not in ip_sessions:
            ip_sessions[ip] = []

    # Build client map from login attempts
    ip_client = {}
    for a in login_attempts:
        ip = a.get('SourceIp')
        c = a.get('Client', '')
        if ip and c:
            ip_client[ip] = c

    for ip, sess in sorted(ip_sessions.items()):
        cmds = sum(len(s['commands']) for s in sess)
        client = ip_client.get(ip, sess[0]['client'] if sess and sess[0]['client'] else 'N/A')
        if do_geo and ip in geo:
            g = geo[ip]
            country = g['country']
            org = g['org'][:40] if g['org'] else 'Unknown'
            lines.append(f"| {ip} | {country} | {org} | {len(sess)} | {cmds} | {client} |")
        else:
            lines.append(f"| {ip} | {len(sess)} | {cmds} | {client} |")
    lines.append("")

    if passwords:
        lines.append("---")
        lines.append("")
        lines.append("## Credentials Attempted")
        lines.append("")
        lines.append("| Password | Attempts |")
        lines.append("|----------|----------|")
        for pw, count in sorted(passwords.items(), key=lambda x: -x[1]):
            lines.append(f"| {pw} | {count} |")
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
            ip = s['ip']
            geo_str = ""
            if do_geo and ip in geo:
                g = geo[ip]
                geo_str = f" - {g['country']}, {g['org']}"
            lines.append(f"### Session {s['id'][:8]} - {ip}{geo_str} ({dur_str})")
            lines.append("")
            lines.append("| # | Command | LLM Response |")
            lines.append("|---|---------|--------------|")
            for i, c in enumerate(s['commands'], 1):
                cmd = c['command'].replace('|', '\\|')
                out = c['output'].replace('\n', ' ').replace('|', '\\|')[:100]
                lines.append(f"| {i} | {cmd} | {out} |")
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
        if not login_attempts and not sessions:
            lines.append("*No attacker login attempts or command execution were recorded for this period.*")
        else:
            lines.append("*No successful logins with command execution yet. Attackers are currently in the brute-force phase.*")
        lines.append("")

    if llm_stats:
        lines.append("---")
        lines.append("")
        lines.append("## LLM Performance")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total LLM calls | {len(llm_stats)} |")
        lines.append(f"| Avg response time | {avg_latency:.0f} ms |")
        lines.append(f"| Avg tokens generated | {avg_tokens:.1f} |")
        min_lat = min(s['total_duration_ms'] for s in llm_stats)
        max_lat = max(s['total_duration_ms'] for s in llm_stats)
        lines.append(f"| Fastest response | {min_lat:.0f} ms |")
        lines.append(f"| Slowest response | {max_lat:.0f} ms |")
        lines.append("")

    if clients:
        lines.append("---")
        lines.append("")
        lines.append("## SSH Client Versions")
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
    if "Cumulative" in date_label:
        lines.append("This cumulative report aggregates all surviving Mumbai telemetry after full regeneration from raw Beelzebub logs (period derived from min and max DateTime across non-excluded events; test traffic from 49.207.63.82, 49.207.60.111, 49.207.58.88 excluded via excluded_ips). Interpret quantitative results separately from infrastructure observations.")
        lines.append("")
        lines.append("### Observation methodology")
        lines.append("")
        lines.append("- **Source:** Surviving Beelzebub JSONL logs on wraith-honeypot (t3.micro, Ubuntu 24.04, ap-south-1), parsed via scripts/generate_report.py (extract_sessions and extract_llm_stats). No log data was altered.")
        lines.append("- **Exclusion:** Researcher-controlled test IPs were excluded during parsing and do not contribute to counts.")
        lines.append("- **Period derivation:** min and max DateTime across non-excluded events; July 1 is validation-only (0 logins, 0 sessions, 6 LLM calls) and excluded from attacker period.")
        lines.append("- **Geo:** Optional ip-api.com lookup for Attacking IPs table (--no-geo skips it); not used to infer attribution.")
        lines.append("")
        lines.append("### Measurement findings (what the honeypot captured)")
        lines.append("")
        if total_commands <= 1 and len(sessions_with_commands) <= 1:
            lines.append(f"- **Source population:** {len(all_ips)} unique observed source IP addresses, {len(sessions)} sessions, {len(login_attempts)} login attempts. Use unique source IPs / observed source addresses / Internet hosts observed - not 773 sophisticated human attackers. SSH client distribution is dominated by SSH-2.0-Go and SSH-2.0-OpenSSH_7.4, consistent with automated scanning and credential-guessing.")
            lines.append(f"- **Engagement depth - core result:** Only {len(sessions_with_commands)} session(s) progressed to post-authentication command execution, with {total_commands} recorded command(s) total (e.g., echo 1 > /dev/null && cat /bin/echo from 47.113.113.162). The deployment therefore primarily captured the scanning / credential-guessing phase with minimal post-authentication interaction.")
            lines.append(f"- **LLM performance under load:** Mean LLM response latency {avg_latency:.0f} ms (avg tokens {avg_tokens:.1f}; {len(llm_stats)} LLM calls) reflects the operational cost of local inference on a t3.micro. Fastest {min(s['total_duration_ms'] for s in llm_stats):.0f} ms, slowest {max(s['total_duration_ms'] for s in llm_stats):.0f} ms. This latency and the July 26 OOM indicate that pure local-LLM terminal emulation was not operationally reliable on this t3.micro configuration under sustained Internet exposure.")
            lines.append("")
        lines.append("### Infrastructure observations (how the deployment behaved)")
        lines.append("")
        lines.append("- **July 26 resource exhaustion and telemetry interruption:** Around 2026-07-26T17:17-17:18Z the local Ollama/qwen2.5:0.5b backend exhausted memory; the Linux OOM killer terminated llama-server (RSS ~629 MB) with systemd-journald and snapd watchdog failures (Out of memory: Killed process ... (llama-server)). Beelzebub did not immediately crash - it continued processing until at least the last confirmed attacker event at 2026-07-26T17:23:56Z. Around 17:44Z the guest reported 169.254.169.254 unreachable, DNS via 127.0.0.53 misbehaving, and SSM agent unable to reach AWS endpoints, while cron/sysstat continued. The best-supported interpretation is resource exhaustion and degraded guest networking that interrupted external honeypot connectivity and stopped telemetry collection. The instance itself remained running July 17 - September 10 and was not intentionally stopped; after the September 10 reboot, SSH 22, honeypot 2222, Beelzebub, and Ollama all recovered normally. Use precise language - OOM condition, resource exhaustion, degraded networking, telemetry interruption - not unqualified server crashed.")
        lines.append("- **Separating findings from infrastructure:** The scanning/credential-guessing result is a measurement finding about Internet SSH activity observed by the honeypot. The OOM/network degradation is an infrastructure observation about the local-LLM deployment's operational limits. They are distinct.")
        lines.append("")
        lines.append("### Observed LLM terminal-emulation limitation")
        lines.append("")
        lines.append("- Shortly before the interruption, source IP 39.105.172.20 (285 sessions on July 26 alone) repeatedly reconnected and issued echo -e \"\\x6F\\x6B\". The Beelzebub LLMHoneypot plugin logged Rate limit exceeded / plugin \"LLMHoneypot\" execute error: rate limited, and the local qwen2.5:0.5b model returned inconsistent, semantically incorrect responses to this trivial command (variants including command not found, malformed explanations, escaped Unicode output). This is documented as an observed limitation of pure LLM-based terminal emulation. It supports Wraith's later hybrid design - deterministic shell behavior for normal Linux commands with the LLM reserved as a controlled fallback/adaptive layer. Rate limiting did not cause the outage; the confirmed infrastructure cause is OOM/resource exhaustion and subsequent network degradation.")
        lines.append("")
        lines.append("### Relationship to Wraith adaptive-shell work")
        lines.append("")
        lines.append("- The Mumbai result motivates Wraith's architecture: keep the SSH honeypot's shell responses deterministic and auditable, and use the LLM only where adaptivity is needed. Mumbai is the Beelzebub + local-LLM baseline (adaptive/interactive path); Wraith (us-east-1, static-shell + structured JSONL telemetry via wraith/server.py and wraith/telemetry.py) is the additive structured-telemetry path that builds directly on the limitations documented here. Wraith's deterministic handling of common commands and its per-session filesystem (wraith/filesystem.py) are intended to avoid the inconsistency and rate limiting observed with pure LLM emulation.")
        lines.append("")
        lines.append("### Limitations of interpretation")
        lines.append("")
        lines.append("- This dataset characterizes the scanning and credential-guessing phase on this single t3.micro deployment; it does not support general claims about all LLM honeypots or all cloud configurations. The single post-authentication session limits conclusions about engagement depth or session persistence.")
        lines.append("- No geographic or human-actor attribution is claimed beyond observed source IPs and SSH client strings (e.g., SSH-2.0-Go, SSH-2.0-OpenSSH_7.4); 773 source addresses should not be read as 773 distinct human attackers.")
        lines.append("- Latency and OOM observations are specific to local qwen2.5:0.5b inference on this t3.micro configuration under sustained Internet exposure and are presented with indicates and was observed language to avoid overstated causal claims.")
        lines.append("")
        lines.append("### Reproducibility and coverage notes")
        lines.append("")
        lines.append("- **Coverage:** 24 dated reports - 2026-07-01.md (validation/LLM testing, 0 attacker events, Period N/A, 6 LLM calls) plus 2026-07-03.md through 2026-07-26.md (attacker-observation period). July 2: no surviving telemetry source, no report. July 5: stale report intentionally deleted (no source). Do not fabricate a July 5 report or attacker activity for July 1.")
        lines.append("- **Generation:** Reports regenerated from raw Beelzebub logs via scripts/generate_report.py with test-IP exclusion and --out-file support for both daily and cumulative modes; --no-geo available for offline regeneration. 2026-07-05.md must remain absent.")
        lines.append("")
        lines.append("*No further attacker telemetry is available after 2026-07-26T17:23:56Z due to the interruption described above.*")
    else:
        if not login_attempts and not sessions:
            lines.append("*No attacker login attempts or command execution were recorded for this period. This is consistent with a pre-observation or validation interval (e.g., LLM testing) rather than active attacker telemetry.*")
        else:
            lines.append("*(Add manual observations here after reviewing the session details above.)*")
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