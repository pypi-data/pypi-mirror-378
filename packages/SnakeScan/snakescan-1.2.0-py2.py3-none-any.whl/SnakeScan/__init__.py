"""Module SnakeScan"""
__version__="1.2.0"
import socket
from art import tprint
from datetime import datetime
from tqdm import tqdm
from termcolor import colored
portsopen=0
portsclosed=0
Run_now=True
Bool=True
boolean=0
OpenPorts=[]
ports = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 43: "WHOIS", 53: "DNS", 80: "http",
    115: "SFTP", 123: "NTP", 143: "IMAP", 161: "SNMP",
    179: "BGP", 443: "HTTPS", 445: "MICROSOFT-DS",
    514: "SYSLOG", 515: "PRINTER", 993: "IMAPS",
    995: "POP3S", 1080: "SOCKS", 1194: "OpenVPN",
    1433: "SQL Server", 1723: "PPTP", 3128: "HTTP",
    3268: "LDAP", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 8080: "Tomcat", 10000: "Webmin" }
def is_port_open(host,port):
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	try:
		#Connecting...
		s.connect((host,port))
		#Port//(Closed<--or-->Open)
	except:
		s.close()
		return False
	else:
		s.close()
		return True
print("–"*60)
tprint("SnakeScan")
print("–"*60)
print(f"{__version__}".rjust(60))
print(f"Skip{colored('|*|','blue')}Error: Host:localhost{colored('|$|','green')}Port:4000 ports")
while Run_now:
	host=input(f"{colored('[$]','green')}Host/Skip-->")
	if host == "Exit"  or host == "exit":
		break
	if host == "":
		print(f"{colored('|*|','blue')}localhost")
		host=socket.gethostbyname(socket.gethostname())		
	port_user=input(f"{colored('[$]','green')}Port/Skip-->")
	port_single=port_user
	if port_user == "Exit" or port_user == "Exit":
		break
	if port_user:
		try:
			length=int(port_user)
		except:
			   if "--s" in str(port_user):
			       port_user=port_single.strip().strip("--s")[1:len(port_user)]
			       for i in range(len(port_user)):
			           if port_user[i] == " ":
			               port_user=port_user[0:i]
			               break
			       port_user=int(port_user)
			       for single in range(1):
			           if is_port_open(host,port_user):
			               print(f"Open{colored('|√|','green')}-->{ports[port_user]}|{port_user}|")
			           else:
			               try:
			                   print(f"Closed{colored('|X|','red')}-->{ports[port_user]}|{port_user}|")
			               except:
			                    print(f"Closed{colored('|X|','red')}-->|{port_user}|")
			  			               
			       continue
			       
			   else:
			      port_user="4000"
			      print(f"{colored('[!]','red')}Port:invalid value")
			      for i in range(0,len(port_user)):
			          if port_user[i] == " ":
			              port_user=4000
			              break
			      port_user=int(port_user)
			      length=port_user
	else:
		print(f"{colored('|*|','blue')}4000")
		port_user=4000
		length=port_user
	print(f"{colored('|!|','red')}Listening {host} please wait...")
#|-----------------Starting---------------------|
	length=int(length)+1
	for port in tqdm(range(1,length)):
						if is_port_open(host,port):
							for name in ports:
									if port == name:
										OpenPorts=[port]
										portsopen+=1
						else:
							portsclosed+=1
						if port_user  != "":
										if int(port_user) == port:
											if port_user == "":
												pass
											elif int(port_user) == port:
												if is_port_open(host,port):
													Bool=True
													boolean+=1
										else:
											Bool=False												
	if boolean == 1:
		pass
	for i in OpenPorts:
		print(f"Open{colored('|√|','green')}-->{ports[i]}|{i}|")
	print(f"{host}".center(60,"-"))
	print(f"Closed{colored('|X|','red')}:{portsclosed}")
	portsclosed=0
	print(f"Open{colored('|√|','green')}:{portsopen}")
	portsopen=0
	print("-"*60) 