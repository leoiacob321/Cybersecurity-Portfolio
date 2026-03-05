# Enumeration
This is the process of extracting usernames, machine names, network resources, shares, and aservices from a system or netowrk. It gives you a structure of the environment you are assesing. 

### Lab Environment
  -  Parrot OS virtual machine
  - Metasploitable virtual machine
  - Windows 11 virtual machine
  - Windows 2022 virtual machine


## NetBIOS Enumeration
This process helps you obtain sensitive information such as list of computers belonging to a target domain, network shares, policies, etc.
NetBIOS stands for Network Basic Input Output System and its used by Windows for file and printer sharing. A NetBIOS name is an unique computer named assigned to Windows systems made up of 16-character ASCII string. First 15 characters are used for the device name and the last character is reserved for the service or name record type.

Here I used nbtstat. I used the Windows 2022 VM to target Windows 11 VM
("-a" displays the NetBIOS name table of the remote computer)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/b57ea829-0e5b-48c6-9492-5a8882681c2c" />



## NFS Enumeration
Here I used the RPCSan script by hegusung (https://github.com/hegusung/RPCScan.git)

(Below we can see that port 2049 is open and the NFS service is running on it)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/554adbd9-0b9e-4106-bc32-dab7a1c9709d" />



## DNS Enumeration
This process locates and lists all possible DNS records for that target domain.

The below dig command on a Linux machine gets information about all the DNS name servers of the target domain and displays it in the ANSWER SECTION.
("ns" below returns name servers in the result for www.x.com)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/d98364e1-3f41-4c5f-a8da-a44c3eae805a" />

Below is used to perform DNS enumeration on Windows DNS servers. I used nslookup for this task.
(entered nslookup interactive mode and used "querytype=soa" which is "Start of Authority" to retrieve administrative info about the DNS zone of the target domain "x.com")

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/2a112d20-15e6-4973-a8c3-fe8bc9786283" />


## SMTP Enumeration
SMTP Enumeration shows the valid list of user accounts on the SMTP server(Simple Mail Transfer Protocol). 

In this task I used nmap scirpt engine (NSE) to enumerate SMTP services running on target system. 
(I am targeting Metasploitable here hence not much information is shown as it has VRFY, EXPN, TURN and no open relay. A fully configured SMTP service would show more information)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/fd68addf-5293-4a6e-ab1f-b8f9fcdd6779" />
