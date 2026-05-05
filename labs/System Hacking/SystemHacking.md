# System Hacking

Walkthrough of the system hacking lifecycle — gaining access, escalating privileges, maintaining persistence, and clearing tracks. All done in a controlled home lab environment.


## Lab Environment
  - Parrot OS VM
  - Metasploitable VM
  - Windows 11 VM




## Gaining Access
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






## Perform Privilege Escalation to Gain Higher Privileges
  -  Horizontal Privilege Escalation: An unauthorized user tries to access the resources, functions, and other privileges that belong to an authorized user who has similar access permissions.
  -  Vertical Privilege Escalation: An unauthorized user tries to gain access to the resources and functions of a user with higher privileges such as an application or site administrator.



 ### Escalate Privileges by Bypassing UAC and Exploiting Sticky Keys.
 Here, I will be exploiting Sticky keys feature to gain access and to escalate privileges on the target.


I ran the following command to generate the payload.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/b8799732-c99e-47b9-870b-2c553cb649c2" />


I created a new directory to share the "finaltry.exe" and copied the .exe into that location using the below commands.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/f74f86a6-8c08-4a8f-8c5d-8fbbe4b63951" />

I started an apache server.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/af20e9b8-a2b7-4697-a0b0-114ceb4417e1" />


I launched Metasploit Frame work using "msfconsole" and typed "use exploit/multi/handler". With this being opened i set the following parameters. This sets up a reverse_tcp payload with the host being the attacker and the listening port as 444.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/ef4033e5-83fb-4d0c-8a79-9d0fb77b094b" />


I switched to my Windows 11 VM and downloaded/ran the finaltry.exe payload.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/7dbb508b-6595-42b4-a0f1-089d1e9a461a" />


Confirm you are in the target machine.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/0f17b8e7-9e06-4c11-8a18-92ed7e3fff41" />


I backgrounded the session using "background" and searched for bypassuac using "search bypassuac" command.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/96836b5a-c3c0-4060-87e6-e3d5878d9b23" />


Here I am using the FodHelper Registry keys to bypass Windows UAC protection.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/fd6d1971-5426-4091-a467-b7b920c25c8a" />


In my lab the privileges were already elevated hence the below result but the "bypassuac_fodhelper" should be able to get you elevated privileges.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/9d00270d-3ad0-4baa-8ffa-2adb258fc71a" />



I will now use the sticky_keys mpdule present in Metasploit to exploit the sticky keys feature in Windows 11.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/30583faa-926a-4ce0-bdbf-eb5dbbb35ac5" />


I pressed SHIFT key to trigger sticky keys and session was established. This gave me elevated privileges.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/dd101328-5692-4c4e-a7c0-f00537a75f82" />


This concludes the demo of maintain presistance by exploit Sticky Keys.



## Maintain Remote Access and Hide Malicious Activities

### Maintain Persistance by Modifying Registry Run Keys
Registry keys labled as Run and RunOnce are made to automatically run programs whe user logs into the system. An attacker can execute persistance attacks if they discover a service connected to a registry key with full permissions.


On Parrot Security VM I generated the tcp payload that will establish a Meterpreter session and a payload that needs to be uploaded to the Run Registry of Windows 11 VM.


<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/715bac0f-7f8a-4181-87f7-5d0849253734" />


Earlier I created a directory to share the files to, "/var/www/html/share", so I will be using this again to transfer the payloads. I copied the files to this location.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/2125264d-3b44-4b71-b354-0295a9aed28b" />


I downloaded both files onto the Windows 11 VM.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/22b9f2e8-3809-47e4-935f-cb13a61da020" />


I ran the "Test.exe" and swithched back to Parrot Security to verify all is working.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/fe36e2a6-8c09-4b22-83cd-7819fc1a9b5f" />


In this task, I will bypass Windows UAC protection via SilentCleanup task present in Windows Task Scheduler.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/d6f0b4d1-9c65-47f3-912e-3d61917bf5b5" />


In an elevated shell session I typed the following command.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/34e323f7-4a9d-489f-ba62-695241ee1f8b" />


In another terminal, I set up another msfconsole and restarted the Windows 11 VM. Once restarted, the session re-establishes itself.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/196bdc36-5f09-4054-bf83-907b696e03b2" />


<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/24d9bee8-4f07-4d7a-ada3-fa05206b6472" />


Every time the Admin restarts the system, the reverse shell is opened. 



## Clearing Logs to hide Evidence
Throughout this lab, I have demonstrated the steps taken by attackers during the system hacking lifecycle. It starts with gaining access to the system, escalating privileges, executing malicious applications and then hiding files. This step focuses on clearing any tracer of the intrusion.


### Clearing Logs from Windows Machines

I opened a Shell as Administrator and ran "wevtutil el" to display a list of event logs ("el" below means "enum-logs")

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/67428bf4-0ae6-4b2d-9398-bf14e07ec74f" />


Then I ran "wevtutil cl system" to clear system logs ("cl" = clear-logs and [system] can be replaced with any log name)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/a2dc84ec-5038-4597-a9ad-f1ca5b9cf245" />



I also used "Cipher" which can be used to encrypt the deleted files on the C: DRIVE.
The Cipher.exe utility starts overwritting the deleted files. The time taken for Cipher to completes depends on the size of the file/folder/drive.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/1174c843-ec28-41ce-a795-9b2057260c66" />

~~End


### Clearing Logs from Linux Machines
On the Parrot Security VM I used the BASH (Bourne Again Shell) which is a sh-compatible shell that stores command history in a file called bash history. You can view saved command history using "~/.bash_history" command.

The commands below are as follows:
  - export HISTSIZE=0: disables the BASH shell from saving the history
  - history -c: clears stored history
  - shred ~/.bash_history: shred the history file
  - more ~/.bash_history: view the shredded history content

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/8bdce8e4-77cf-416a-9bc8-13e788727f48" />

~~End
