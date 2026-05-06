#!/usr/bin/env python3
# autorecon — nmap-driven recon that auto-runs port-specific enumeration

import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

HTTP_PORTS = (80, 443, 8080, 8180, 8443)
SMB_PORTS = (139, 445)


def run(cmd, out_file=None):
    print(f"    > {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    if out_file:
        with open(out_file, "w") as f:
            f.write(output)
    return output


def nmap_scan(target, out_dir):
    print(f"[*] nmap scan — {target}")
    xml_out = f"{out_dir}/nmap.xml"
    run(f"nmap -sV -sC -O --open -oX {xml_out} -oN {out_dir}/nmap.txt {target}")
    return xml_out


def parse_nmap(xml_file):
    ports = []
    try:
        root = ET.parse(xml_file).getroot()
        for port in root.findall(".//port"):
            state = port.find("state")
            if state is None or state.get("state") != "open":
                continue
            svc = port.find("service")
            ports.append({
                "port": int(port.get("portid")),
                "proto": port.get("protocol", "tcp"),
                "service": svc.get("name", "unknown") if svc is not None else "unknown",
                "product": svc.get("product", "") if svc is not None else "",
                "version": svc.get("version", "") if svc is not None else "",
            })
    except Exception as e:
        print(f"[!] nmap XML parse error: {e}")
    return ports


def enum_smb(target, out_dir):
    print(f"[*] SMB enumeration — {target}")
    run(f"nxc smb {target} --shares 2>/dev/null", f"{out_dir}/smb-shares.txt")
    run(f"nxc smb {target} --users 2>/dev/null", f"{out_dir}/smb-users.txt")
    run(f"enum4linux -a {target} 2>/dev/null", f"{out_dir}/enum4linux.txt")


def enum_http(target, port, out_dir):
    proto = "https" if port in (443, 8443) else "http"
    print(f"[*] HTTP enumeration — {proto}://{target}:{port}")
    run(f"curl -skI {proto}://{target}:{port}/", f"{out_dir}/http-{port}-headers.txt")
    run(f"nikto -h {proto}://{target}:{port} -nointeractive 2>/dev/null", f"{out_dir}/nikto-{port}.txt")


def enum_ftp(target, out_dir):
    print(f"[*] FTP check — {target}:21")
    run(f"nmap -p 21 --script ftp-anon,ftp-syst,ftp-bounce {target}", f"{out_dir}/ftp.txt")


def enum_smtp(target, out_dir):
    print(f"[*] SMTP enumeration — {target}:25")
    run(f"nmap -p 25 --script smtp-enum-users,smtp-commands {target}", f"{out_dir}/smtp.txt")


def enum_ssh(target, out_dir):
    print(f"[*] SSH banner — {target}:22")
    run(f"nmap -p 22 --script ssh2-enum-algos,sshv1 {target}", f"{out_dir}/ssh.txt")


def generate_report(target, ports, out_dir, start):
    elapsed = (datetime.now() - start).seconds
    out = f"# Recon Report — {target}\n\n"
    out += f"**Date:** {start.strftime('%Y-%m-%d %H:%M')}  \n"
    out += f"**Duration:** {elapsed}s\n\n---\n\n"
    out += "## Open Ports\n\n"
    out += "| Port | Protocol | Service | Version |\n|---|---|---|---|\n"
    for p in ports:
        ver = f"{p['product']} {p['version']}".strip()
        out += f"| {p['port']} | {p['proto']} | {p['service']} | {ver} |\n"
    out += "\n---\n\n## Enumeration Files\n\n"
    for fname in sorted(os.listdir(out_dir)):
        if fname != "report.md":
            out += f"- `{fname}`\n"
    out += "\n---\n\n## Notes\n\n"

    report_path = f"{out_dir}/report.md"
    with open(report_path, "w") as f:
        f.write(out)
    print(f"[+] Report → {report_path}")


def main():
    parser = argparse.ArgumentParser(description="autorecon — nmap + port-based enumeration")
    parser.add_argument("target", help="target IP or hostname")
    parser.add_argument("-o", "--output", default=None, help="output directory (default: recon_<target>_<timestamp>)")
    args = parser.parse_args()

    start = datetime.now()
    out_dir = args.output or f"recon_{args.target}_{start.strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(out_dir, exist_ok=True)

    print(f"[*] Target: {args.target}")
    print(f"[*] Output: {out_dir}/")

    xml_file = nmap_scan(args.target, out_dir)
    ports = parse_nmap(xml_file)

    if not ports:
        print("[!] No open ports found — check the target is up and nmap ran cleanly.")
        sys.exit(1)

    print(f"[+] {len(ports)} open port(s): {[p['port'] for p in ports]}")

    smb_done = False
    for p in ports:
        port = p["port"]
        if port in SMB_PORTS and not smb_done:
            enum_smb(args.target, out_dir)
            smb_done = True
        elif port in HTTP_PORTS:
            enum_http(args.target, port, out_dir)
        elif port == 21:
            enum_ftp(args.target, out_dir)
        elif port == 25:
            enum_smtp(args.target, out_dir)
        elif port == 22:
            enum_ssh(args.target, out_dir)

    generate_report(args.target, ports, out_dir, start)
    print(f"[+] Done ({(datetime.now() - start).seconds}s)")


if __name__ == "__main__":
    main()
