from scapy.all import sniff
from .features import update_flow

def packet_handler(packet, callback):
    result, src_ip = update_flow(packet)

    if result is not None:
        callback(result, src_ip=src_ip)


def capture_packets(callback):
    print("Starting packet capture...")
    sniff(prn=lambda pkt: packet_handler(pkt, callback), store=False)
