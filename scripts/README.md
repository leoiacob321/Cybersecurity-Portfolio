# Scripts

Custom scripts written to automate parts of the penetration testing process.

---

## autorecon.py

Automated recon tool that runs an nmap service scan against a target, parses the results, and chains the right enumeration tool for each open port. Saves all output to a timestamped directory and generates a markdown report.

**Usage:**
```bash
sudo python3 autorecon.py <target>
sudo python3 autorecon.py <target> -o <output_dir>
```

**Example:**
```bash
sudo python3 autorecon.py 10.10.10.20
```

**What it does per port:**

| Port(s) | Tool |
|---|---|
| 21 | nmap ftp-anon, ftp-syst, ftp-bounce scripts |
| 22 | nmap ssh2-enum-algos, sshv1 scripts |
| 25 | nmap smtp-enum-users, smtp-commands scripts |
| 80, 443, 8080, 8180, 8443 | curl headers + nikto |
| 139, 445 | nxc (shares + users) + enum4linux |

**Output folder contains:**
- `nmap.txt` / `nmap.xml` — full nmap scan results
- `smb-shares.txt`, `smb-users.txt`, `enum4linux.txt` — SMB enumeration
- `ftp.txt`, `ssh.txt`, `smtp.txt` — per-service nmap script output
- `http-<port>-headers.txt`, `nikto-<port>.txt` — web enumeration
- `report.md` — summary with open ports table and file index

**Tested against Metasploitable 2 — found 23 open ports and ran 8 enumeration modules in 81 seconds.**

**Requirements:** nmap, nxc (netexec), enum4linux, nikto — all available on Parrot OS / Kali by default.
