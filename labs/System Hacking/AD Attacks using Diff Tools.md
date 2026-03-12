
# Overview

## Perform Active Directory Attacks Using Different Tools

This involves exploiting vulnerabilities withing AD's infrastructure. These can include password spraying, Kerberoasting, and exploiting configurations


# Objectives

  - Perform Intial scans to obtain DC IP and Domain name
  - Perform AS-REP roasting attack
  - Spray cracked password into network using CrackMapExec


# Lab Environment

  - Parrot Security VM
  - Windows 2022
  - Windows 11
  



## Peform Initial Scans to Obtain Domain Controller IP and Domain Name

I ran "nmap 10.0.0.0/24" command to scan the entire subnet and identify the DC IP address. Nmap shows that host "10.0.0.30" has port "88/TCP kerberos-sec" and port "389/TCP ldap" which confirms that this ir our DC IP address.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/38429b08-31ed-4306-8baf-2c2cd77c2a65" />


I then ran a more aggresive scan to get more information. This gave me the domain name as shown in the screenshot below. This can be used in the AS-REP Roasting attack.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/2e9753ec-39e8-425f-8c9a-31daf6256dd6" />


## Perform AS-REP Roasting Attack

ASP-REP roasting attack targets user accounts in AD that do not require Kerberos pre-authentication. Attackers can request a ticket granting ticket (TGT) for these accounts without needing the user's password.

I navigated to "impacket/examples" folder. I then ran the below command.
  - GetNPUsers.py: Python script to retrieve AD user info
  - lab.local/: Target AD domain
  - no-pass: Flag to find user accounts not requiring pre-auth
  - -userfile: Path to the file with user account list(created one with random names)
  - -dc-ip 10.0.0.30: DC IP

From the inital command, I got no hashes as both users had pre-auth set.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/46522561-dfc9-4dcd-95b7-4ebc84a6ee05" />


What I did was log onto the DC and created a vulnerable user using:

(New-ADUser -Name "joshua" -SamAccountName "joshua" -AccountPassword (Read-Host -AsSecureString "Enter Password") -Enabled $true -PasswordNeverExpires $true -DoesNotRequirePreAuth $true)

We can see now that we created a new user and "DoesNotRequirePreAuth" is set to "True"

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/690d5bf0-8cc0-4912-9e3d-8e3926e38f4b" />


When I ran the command again, I obtained joshua's password hash.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/b97e87e7-35b2-40f8-a93c-0c31d236379c" />


I copied the hash into a .txt file and used "John the Ripper" like shown below to get the password hash in plain text.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/864cf177-fb29-459c-9f28-8a19a4f8263c" />


~~End


 ## Spray Cracked Password into Network using NetExec

 If "qwerty" is a cracked password, NetExec can be used to test this password against numerous user accounts and services accross a network.

 
