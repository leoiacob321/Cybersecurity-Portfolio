# Footprinting and Reconnaissance
Footprinting and recon refers to collecting as much information as possible regarding a target network from publicly accessible source. This is the first step when you're thinking about attacking a target. 
Attackers use this to create a "blueprint" of the target organisation. 


## Performing Footprinting through search engines.
"intitle:login site:x.com"
This command uses intitle and site Google advanced operators, which restrict results to pages on the x.com website that contain the login pages. Example in below screenshot

<img width="500" height="500" alt="Screenshot 2026-02-25 152359" src="https://github.com/user-attachments/assets/72eed13b-6fe6-4e26-acc6-0ac0f113fa96" />

### Note: This Google search operator can help attackers to extract login pages of the target organisation which can be later used for various attacks such as bruteforcing or injection attacks.


There are other Google operators which you can also use to perform advanced searches to gather more information:
cache:www.x.com - Query returns cached version of the website www.x.com
allinurl: Facebook career - Query returns only pages with the words "Facebook" and "career" in URL




## Perform Footprinting through internet reserach services
Internet Search Engines are online applications which provide a variety of publicly accessible information related to the target organisation.

Here we are using netcraft to aquire information about "www.Facebook.com"
Navigate to "https://sitereport.netcraft.com/" and type in your target site (here we are using https://www.facebook.com)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/ef6a88a3-9b58-49de-92e1-35ae6484c782" />

Here we can see a bunch of information about the target (Background, Network IPs etc).

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/d479b3cd-1f26-40f9-954e-299505afa56a" />



You can obtain DNS servers along with Geo IP using DNSdumpster.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/4573973c-1c6f-4c98-801a-de7724fdecf0" />


Here you can find a list of DNS Servers, MX Records, Host records along with IP addresses and domain mapping. You can also download an xlsx. of this information 

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/e520a20f-8f24-41c9-9030-d779f4bf64ed" />



## Footprinting through Social Networking sites
Here we are using Sherlock (python-based tool) to gather information about a person. Sherlock scans a great number of social networking sites and pulls information about the given person.

Run "sherlock "Bill Gates" command to get all related URLs to Bill Gates.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/6b6a366b-7f80-46b7-b4de-3b4b3b0f966c" />



## DNS Footprinting
Attackers use DNS(Domain Name System) footprinting to gather information about the DNS server, DNS records and types of servers used by the target.
For this task, I will be using "nslookup" tool to query the DNS to obtain domain name and IP address mapping.
Run nslookup command to initiate the tool.
In the interactive mode, type set type=a and press Enter. This sets the type as "a" to query for the IP address of the given domain.
Type the target domain (here we are using www.facebook.com) and press Enter. This resolves the IP address and displays results

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/0e2d7ffa-e4c3-45f6-a881-5c7823a3faeb" />

Use "set type=MX" to show mail exchange servers for the domain:

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/c8eaa11f-66c3-452c-ad07-6b7adc6e085f" />

Below is a list of nslookup commands:

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/fdd8ecee-9424-40b3-8817-4268ea27fc13" />



## Network Tracerouting in Windows machine
Network tracerouting enables us to map the network topology of the organisation by identifying the path and hosts lying between the source and destination. Also useful to extract info about the geo location of routers, servers, and IP devices in a network.

Traceroute can also be useful for MITM(man-in-the-middle) attacks as we can see what path the packets are travelling through.

run tracert <target_domain> on Windows.

<img width="200" height="200" alt="image" src="https://github.com/user-attachments/assets/dd17219f-6e4f-4af9-a3c6-3814bd8158b3" />

run traceroute <target_domain> on Linux.
In the below example, we do not see any replies because there was no ICMP response recieved for the probe. Some reasons why this might happen are: router/firewall blocks ICMP, the hop is configured not to reveal itself, the hop is too busy to respond, UDP/ICMP is fileterd. 

<img width="200" height="200" alt="image" src="https://github.com/user-attachments/assets/969ab862-3861-4f5c-bc1c-af0e30bbc51d" />

You can try the following options to fix this: 
Use ICMP instead of UDP - sudo traceroute -I <target>
Use TCP (often works better through firewalls) - sudo traceroute -T <target>


## Recon-dog
Recon-dog is an all-in-one tool for all basic info gathering needs. Below are the features of Recon-dogpyt

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/53596596-35d2-415a-b08c-b7ece218b042" />

Below is also an example of the "All" feature in Recon-dog that applies all features in one go.

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/c378ee13-2a57-45a1-9820-3c2b498370a2" />



