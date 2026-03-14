# My Wazuh Home Lab Setup – Ubuntu Manager




Documenting how I got Wazuh running in my home lab so I (or future me) don't have to google the same stuff again.

Goal was simple: one Ubuntu VM as the central Wazuh manager + indexer + dashboard, and a Windows 11 VM as an agent sending logs/alerts back to it.  
Ended up being way more painful than I expected because of VirtualBox networking nonsense, but it works now.

## Overview

- **Manager**: Ubuntu 24.04 LTS VM (all-in-one: manager, indexer, dashboard)
- **Agent**: Windows 11 Pro VM
- **Hypervisor**: VirtualBox (because I'm cheap and it's what I already had)
- **Networking**: Adapter 1 = Internal Network (lab-only comms), Adapter 2 = NAT (internet)
- **IPs used**:
  - Ubuntu manager (Internal): 10.0.0.50
  - Windows 11 agent (Internal): 10.0.0.40
 

## What Actually Worked

### 1. Ubuntu – Install Wazuh All-in-One (manager + indexer + dashboard)

Used the official all-in-one deployment script – easiest way for a lab.

```bash
curl -sO https://packages.wazuh.com/4.x/wazuh-install.sh && sudo bash ./wazuh-install.sh -a
```

  - Takes ~10–15 minutes depending on your VM specs.
  - At the end it prints the admin password – save it somewhere safe (you'll need it for the web UI).
  - Dashboard lives at https://<ubuntu-ip> (self-signed cert, so browser will complain – just accept it).


Firewall note:

  I had to open a few ports manually with ufw because the script doesn't do everything:bash

- sudo ufw allow 1514/tcp   # agent communication
- sudo ufw allow 1515/tcp   # agent enrollment
- sudo ufw allow 443/tcp    # dashboard
- sudo ufw reload



### 2. Networking Hell

(the part that took forever)VirtualBox Internal Network is great for isolation but default settings make VMs invisible to each other. What finally worked: Both VMs → Adapter 1: Internal Network, same exact name (e.g. lab-int)
Adapter 1 Promiscuous Mode: Allow All on both VMs (this was the magic fix)
Static IPs on Adapter 1 (Internal):Ubuntu: 10.0.0.50/24
Windows: 10.0.0.40/24

No gateway/DNS on Internal adapter (internet comes from NAT adapter)
Windows Firewall: Allow ICMP (ping) inbound:
~~~
netsh advfirewall firewall add rule name="Allow ICMPv4-In" protocol=icmpv4:8,any dir=in action=allow
~~~

After this, ping worked both ways – huge relief.



### 3. Windows 11

– Install & Connect the AgentManual way because the fancy PowerShell one-liners kept 403-ing on me:Downloaded the MSI manually in browser:
https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.3-1.msi
Installed from elevated PowerShell (adjust path):
~~~
msiexec.exe /i "C:\Users\YourUser\Downloads\wazuh-agent-4.14.3-1.msi" /q WAZUH_MANAGER="10.0.0.15"
~~~

Waited 1–2 minutes, refreshed dashboard → agent appeared as Active 

If it doesn't connect, check:
  -  C:\Program Files (x86)\ossec-agent\ossec.log for errors
  -  Make sure Windows can reach 10.0.0.15:1515 (enrollment) and :1514 (normal comms)


### 4. First Look at the Dashboard
Login: https://10.0.0.15 (user: admin, password from install output)
Agents → should see your Windows machine
Security events → Windows logons, process creations, etc. start flowing in
Add Sysmon later for way better visibility (not done yet in this setup)


### Lessons Learned / GotchasAlways
  - Use the Internal IP (10.0.0.50) for agent config – not the NAT one (10.0.3.x)
  - Promiscuous Mode = Allow All is almost always needed for Internal Network ping to work
  - Save the dashboard password immediately – recovering it later is annoying
  - Test ping both ways before even attempting agent install
  - If agent says "Unable to connect to enrollment service" (error 1208), 99% chance it's wrong IP or port 1515 blocked

