# System Hacking
System hacking is the practice of exploiting vulnerabilities in a computer system to gain unauthorized access, escalate privileges, or manipulate system behavior. In cybersecurity, it can be performed by malicious attackers or by ethical hackers who test systems to strengthen defenses.


## Overview
In this lab, I focused on the practical techniques attackers use to compromise operating systems and gain control over a target machine. My goal was to walk through the full system‑hacking lifecycle from the perspective of an ethical hacker: identifying weaknesses, exploiting them, escalating privileges, and analyzing the impact of the compromise.
Throughout the exercise, I worked hands‑on with authentication mechanisms, password attacks, privilege escalation paths, and post‑exploitation techniques. By simulating real‑world attacker behavior in a controlled environment, I strengthened my understanding of how system‑level breaches occur and how defenders can detect and prevent them.
This lab allowed me to apply both offensive and defensive thinking, reinforcing my ability to evaluate system security from an attacker’s point of view while maintaining an ethical, structured methodology.


## Objectives
The objective of this lab was to demonstrate my ability to compromise a system ethically, document each stage of the attack, and analyze the security implications. Specifically, I aimed to:
  - Perform targeted enumeration to identify system vulnerabilities.
  - Execute password‑based attacks to gain initial access.
  - Successfully authenticate to the target system using recovered credentials.
  - Escalate privileges to administrative/root level.
  - Extract sensitive information such as password hashes or system configuration data.
  - Understand how attackers maintain persistence and cover their tracks.
  - Reflect on defensive controls that could prevent or detect each step.
By completing this lab, I strengthened my practical skills in system exploitation, improved my understanding of attacker workflows, and gained experience documenting findings in a professional, security‑focused format.


## Lab Environment
  - Parrot OS VM
  - Metasploitable VM
  - Windows 11 VM



### Gaining Access
LLMNR (Link Local Multicast Name Resolution) and NBT-NS (NetBIOS Name Service) are two main elements of Windows OSes that are used to perfrom name resolution for hosts present on the same link.

I used Responder. which is a LLMNR, NBT-NS, and MDNS poisoner, to extract information such as the target OS version, client version, NTLM client IP, and NTML username and password hash.

(Below shows how to initiate Responder. -I specifies the interface).

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/570348ef-88a5-48f3-ae13-495aca282a31" />

Responder starts listening on the network interface for events.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/903aaa83-1da7-4e0c-a860-aeb3eafee633" />


I ran \\Tools on the Windows 11 VM, and clicked ok.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/093a1926-1b07-4dfd-8fa7-4481ad148ff2" />


Responder starts caputring the access logs of the Windows 11 machine. Responder stores the logs in /usr/share/responder/logs

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/aec8ab20-43a2-4c08-bf42-afa56ebc1a0a" />


Copy the hashes in pluma test editor using "pluma hash.txt" and paste them in.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/ee97b2d8-fd1d-4554-bae0-dbe74d2fdda3" />

I then used John the Ripper (john) to start cracking the password hashes and display the password in plain text.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/65507dff-925f-4a2b-bfea-20e05cf80598" />

# FINISH THIS

### Gain Access to System using Reverse Shell Generator 
A reverse shell generator is a tool that creates a payload designed to make a target machine connect back to an attacker’s machine, giving the attacker an interactive shell.


I used "Reverse Shell Generator" to generate a MSFVenom payload.
(Below we have "IP: 10.0.0.10" which is the listener and "Port: 4444" as the listener port)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/9cff56ee-dc55-4561-8df3-76ee18b499b9" />

Then I switched to my terminal and pasted the command.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/a5d05310-3555-4e0c-a292-1a9ac45f0182" />

Then I generated a code to start the listener and pasted into my terminal.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/547cae9d-a1a6-40a0-bead-b08e9db6b3dd" />

I copied the reverse.exe file from Parrot OS VM to Windows 11 VM using a Python HTTP Server. Windows Security also kept blocking the reverse.exe file from being extracted so I had to create a folder in C:\ with Exclusion persmissions for that folder.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/6e18f9f2-e711-43d2-857a-0f77b8377fe9" />





#FINISH

### Perform Privilege Escalation to Gain Higher Privileges
  -  Horizontal Privilege Escalation: An unauthorized user tries to access the resources, functions, and other privileges that belong to an authorized user who has similar access permissions.
  -  Vertical Privilege Escalation: An unauthorized user tries to gain access to the resources and functions of a user with higher privileges such as an application or site administrator.



 ### Escalate Privileges by Bypassing UAC and Exploiting Sticky Keys.
 


