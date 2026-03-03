# Network Scanning
Network Scanning is a process used to identify active devices, open ports, and services on a network to assess security, map topology, or find vulnerabilities.

In this lab I will be using Parrot OS to do Network Scanning on a Metasploitable machine with different tools like namp cli and Zenmap (GUI for nmap). 

## Host Discovery
This is the process of identifying active hosts in the target network.

### ARP Ping Scan
This is a network discovery technique that sends Address Resolution Protocol (ARP) requests to devices on a local area network (LAN) to identify active hosts.

This scan shows that the host is up. (the -sn command disables port scan and -PR command performs ARP ping scan)

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/02222521-9f0a-4ca1-9262-059db6f2573e" />


### ICMP ECHO Ping Scan
The ICMP ECHO ping scan sends ICMP ECHO requests to a host and if the target host is live, it will retrn an ICMP ECHO reply. Thi is useful for locating active decives or determining if the ICMP is passing through a firewall

(-PE command performs ICMP ECHO ping scan)

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/99764ad8-ec60-4890-ad22-15e883ef3e64" />

You can also use an ICMP ECHO ping sweep to discover list hosts from a range of target IP addresses. (From the below screenshot you can see that the target IP address range is 20-23)

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/37b1071f-6946-4311-8213-905fbb443b89" />



There are a number of other scanning techniques to perform a host discovery on a target network.
  - TCP SYN Ping Scan: nmap -sn -PM <target IP address>
  - TCP ACL Ping Scan: nmap -sn -PA <target IP address>
  - IP Protocol Ping Scan: nmap -PO <target IP address>



## Port and Service Discovery
The next step after discovering live hosts in the target network is to scan open ports and services running on the target IP address in the target network.


### TCP Connect/FULL-Open Scan
TCP connect scan completes a three-way handshake with the target machine. The client sends a SYN packet, which the recipient replies with SYN+ACK packets and in turn, the client acknowledges the SYN+ACK packet with an ACK packet to complete the connection.

(-sT performs TCP full open scan, -v enables verbose output to include all host and ports in output)

<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/37b6bad4-f133-4dea-a655-85b1633af198" />



### Stealth Scan (Half-Open Scan)
This stealth scan involves resetting the TCP connection between client and server abruptly before completing the three-way handshake. This technique can be used to bypass firewall rules and logging mechanisms.

<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/904e6666-5455-456d-9e4a-31b4faffab3c" />


### Xmas Scan
Xmas scan sends a TCP frame to a target system with FIN,URG, and PUSH flags set. If the target has opened the port you will recieve no response and if the target has closed the port, then you will recieve a target system reply with RST.

<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/aab2b9d0-d674-4b5f-8925-b766ff773b65" />


You can also use Zenmap GUI for the nmap security scanner.


### ACK flag probe scan
This technique sends an ACK probe packet with a random sequence number. no response implies that the port is filtered and an RST reponse means that the port is not filtered.

<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/aa7982c5-9c16-4576-a1a7-495514c3aeb1" />


There are also a lot of useful options in the "Profile" section of Zenmap. (Below is a quick scan).

<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/1998ec88-788c-4f30-94a7-9dc0b10a1b37" />



## OS Discovery
Banner grabbing or OS fingerprinting is used to find the OS running on the target.

There are 2 types of banner grabbing techniques.
  - Active Banner Grabbing: Crafted packets are sent to the target and the reponses are noted. These are then compared with a database to determine the OS.
  - Passive Banner Grabbing: This involves collecting service or system information without directly interacting with the target, usually by observing existing network traffic or metadata rather than sending probes. It avoids detection because the target never receives crafted requests.


### OS Discovery using Nmap and Nmap Script Engine (NSE)

The results below display open ports and running services along with their versions and target details such as OS, computer name, NetBIOS computer name, etc.
(-A command performs an aggressive scan. The target here is Metasploitable)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/d993dffb-cc9b-4e2b-a010-18698a50e846" />


<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/528c7b3a-9cf9-4cdb-b12e-bb961a13f1af" />



The results below display information about open ports, respective services running on the open ports along with the name of the OS runnig on the target system.
(-O command performs OS discovery)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/710a0851-7bac-4704-b1ca-f641be5840f9" />


### NSE
(--script command specifies the customised script and smb-os-discovery.nse attempts to determing the OS, computer name, domain, workgroup and current time over the SMB protocol(ports 445, or 139))

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/e0ad4ac8-4aa3-4f0a-ac9b-8639e5d073f5" />




## Scan beyond IDS and Firewall
This is the process of sending packets to the target system in order to bypass perimeter security. This involves using techniques such as fragmentation, source port manipulation and using non-standard ports to evade detection.


### Fragmentation
Paket fragmentation refers to spliting of a probe packet into several smaller packets.

In the screenshot below, I captured packets from the Parrot OS to a Windows 11 VM machine using Wireshark. The screenshot shows the fragmented packets being sent from source to destination

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/faaf1d8e-9c6b-4315-801a-229dc0384fd9" />

The nmap command used for this is show below:
(-f is used to split the IP packets into tiny fragment packets)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/b6dd1869-8a77-46b3-8e9a-f2e341f76a0c" />


### Source Port Manipulatiom
This is when attackers modify the source port field in outgoing packets. Because many firewalls and IDS make decisions based on port numbers, changing this to a common or "trusted" port make the packets bypass the rules in place. (e.g. 53 for DNS, 443 for HTTPS)

The captured packets below show that port number 80 is used to scan other ports of the target.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/01ff535a-1b03-4ec6-9df2-e670ad9bfd70" />


The nmap command used for this is show below:
(-g or --source-port performs source port manipulation)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/57a5823f-19b5-4617-8ae7-abb87e8c9c90" />




## Using Metasploit for Network Scanning

In this example I will use Metasploit to perform a SYN scan on the target(Windows 11 VM).

Use "msfconsole" to start Metasploit and "search" option to find exploits, payloads, auxiliaries and modules by name, CVE, platform or keyword.

<img width="450" height="450" alt="image" src="https://github.com/user-attachments/assets/4d7c099d-346a-4cbf-a446-ade5d68ef630" />


I will be using the auxiliary/scanner/portscan/syn module for this example to perform SYN scan on the target. Select this by typing "use auxiliary/scanner/portscan/syn".
Use "options" to show all configurable settings for the module currently in use. We will configure as show below. ("PORTS" specifies ports scan e.g 20-25, 80, 100-900, "RHOSTS" specifies that target address, "THREADS" controls how many parallel execution threads a module uses (default 1))
Results below show that 1 host was scanned and no port 80 was found on active host.

<img width="450" height="450" alt="image" src="https://github.com/user-attachments/assets/11ed6873-6c46-4d82-ae6f-e0b99724d647" />



I also performed a TCP scan for open ports on target Metasploitable VM.
In this example i used the "auxiliary/scanner/portscan/tcp". The below screenshot displays all open TCP port on the target.

<img width="450" height="450" alt="image" src="https://github.com/user-attachments/assets/e961fb10-568d-449d-a293-8309a01f84e1" />

