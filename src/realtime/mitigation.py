import os
import platform

# keep track of already blocked IPs
blocked_ips = set()


def block_ip(ip):
    """
    Automatically block malicious IP
    Works for Windows and Linux
    """

    if ip in blocked_ips:
        return  # avoid duplicate rules

    system = platform.system()

    try:
        if system == "Windows":
            # Windows Firewall
            cmd = f'netsh advfirewall firewall add rule name="IDS_Block_{ip}" dir=in action=block remoteip={ip}'
            os.system(cmd)

        elif system == "Linux":
            # iptables
            cmd = f"sudo iptables -A INPUT -s {ip} -j DROP"
            os.system(cmd)

        else:
            print("Unsupported OS for auto-blocking")
            return

        blocked_ips.add(ip)
        print(f"[MITIGATION] Blocked IP: {ip}")

    except Exception as e:
        print("Blocking error:", e)
