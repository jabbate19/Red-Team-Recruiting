from scapy.all import get_if_hwaddr, send, ARP
import ipaddress

print("Input Interface: ", end="")
iface = input()
mac = get_if_hwaddr(iface)

print("Input IP or IP Range to Block: ")
ips = input()
slash = ips.find("/")
ip_list = []
if slash == -1:
    ip_list.append(ips)
else:
    ip_list = [str(ip) for ip in ipaddress.ip_network(ips)]

for ip in ip_list:
    