#!/usr/bin/env python3
"""
Samsung Device Finder - Windows Edition
Scans the local network to detect Samsung devices.
Works on Windows 10/11 with Python 3.7+
"""

import sys
import os
import socket
import ipaddress
import subprocess
import concurrent.futures
import re
import time
from datetime import datetime

# Enable ANSI colors on Windows
os.system("color")

# Samsung OUI prefixes
SAMSUNG_OUI = [
    "00:00:f0", "00:01:30", "00:02:78", "00:07:ab", "00:09:18",
    "00:0d:e5", "00:0f:61", "00:12:47", "00:13:77", "00:15:b9",
    "00:16:6b", "00:16:db", "00:17:c9", "00:17:d5", "00:18:af",
    "00:1a:8a", "00:1b:98", "00:1c:43", "00:1d:25", "00:1e:e1",
    "00:1f:cc", "00:21:19", "00:21:d1", "00:23:39", "00:23:d7",
    "00:24:54", "00:24:90", "00:25:66", "00:26:37", "00:e0:64",
    "08:08:c2", "08:d4:2b", "08:ec:f5", "08:fc:88", "0c:14:20",
    "10:1d:c0", "10:30:47", "10:d5:42", "14:49:e0", "14:a3:64",
    "18:3a:2d", "18:67:b0", "1c:5a:6b", "1c:af:05", "20:13:e0",
    "20:6e:9c", "24:4b:03", "28:ba:b5", "2c:ae:2b", "30:07:4d",
    "34:14:5f", "34:c3:ac", "38:0a:94", "38:16:d1", "3c:8b:fe",
    "40:0e:85", "44:78:3e", "48:44:f7", "4c:3c:16", "50:32:75",
    "50:a4:c8", "54:88:0e", "58:ef:68", "5c:0a:5b", "60:6b:bd",
    "64:77:91", "68:eb:ae", "6c:2f:2c", "70:f9:27", "74:45:8a",
    "78:40:e4", "7c:11:be", "80:18:a7", "84:25:db", "84:55:a5",
    "88:32:9b", "8c:71:f8", "90:18:7c", "94:35:0a", "94:63:d1",
    "98:0c:82", "98:52:b1", "9c:3a:af", "a0:07:98", "a0:0b:ba",
    "a4:07:b6", "a8:06:00", "ac:36:13", "b0:47:bf", "b4:07:f9",
    "b8:5e:7b", "bc:20:a4", "bc:44:86", "c0:bd:d1", "c4:42:02",
    "c8:ba:94", "cc:07:ab", "d0:17:c2", "d0:59:e4", "d4:87:d8",
    "d8:57:ef", "dc:71:96", "e0:99:71", "e4:12:1d", "e8:03:9a",
    "ec:1f:72", "f0:25:b7", "f4:7b:5e", "f8:04:2e", "fc:00:12",
]

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
DIM    = "\033[2m"


def banner():
    print(f"""
{CYAN}{BOLD}
 ███████╗ █████╗ ███╗   ███╗███████╗██╗   ██╗███╗   ██╗  ██████╗
 ██╔════╝██╔══██╗████╗ ████║██╔════╝██║   ██║████╗  ██║██╔════╝
 ███████╗███████║██╔████╔██║███████╗██║   ██║██╔██╗ ██║██║  ███╗
 ╚════██║██╔══██║██║╚██╔╝██║╚════██║██║   ██║██║╚██╗██║██║   ██║
 ███████║██║  ██║██║ ╚═╝ ██║███████║╚██████╔╝██║ ╚████║╚██████╔╝
 ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
          {YELLOW}Device Finder — Windows Edition{RESET}
""")


def get_all_interfaces():
    """Get all active network interfaces on Windows using ipconfig."""
    interfaces = []
    try:
        output = subprocess.check_output(
            ["ipconfig"], stderr=subprocess.DEVNULL
        ).decode(errors="ignore")

        current_adapter = None
        for line in output.splitlines():
            # Detect adapter name
            if line and not line.startswith(" "):
                current_adapter = line.strip().rstrip(":")
            # Detect IPv4
            if "IPv4 Address" in line:
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if match:
                    ip = match.group(1)
                    # Skip loopback and APIPA
                    if not ip.startswith("127.") and not ip.startswith("169.254."):
                        subnet = ip.rsplit(".", 1)[0] + ".0/24"
                        interfaces.append({
                            "name": current_adapter or "Unknown",
                            "ip": ip,
                            "subnet": subnet
                        })
    except Exception:
        pass

    # Fallback
    if not interfaces:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            interfaces.append({
                "name": "Default Interface",
                "ip": ip,
                "subnet": ip.rsplit(".", 1)[0] + ".0/24"
            })
        except Exception:
            pass

    return interfaces


def ping_host(ip):
    """Ping a host on Windows."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "300", str(ip)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False


def get_arp_table():
    """Return ARP cache as dict {ip: mac} — Windows format."""
    arp = {}
    try:
        output = subprocess.check_output(
            ["arp", "-a"], stderr=subprocess.DEVNULL
        ).decode(errors="ignore")
        for line in output.splitlines():
            # Windows ARP format: 192.168.1.1    aa-bb-cc-dd-ee-ff    dynamic
            match = re.search(
                r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f]{2}[:\-][0-9a-f]{2}[:\-][0-9a-f]{2}[:\-][0-9a-f]{2}[:\-][0-9a-f]{2}[:\-][0-9a-f]{2})",
                line, re.IGNORECASE
            )
            if match:
                ip_addr = match.group(1)
                mac_addr = match.group(2).replace("-", ":").lower()
                arp[ip_addr] = mac_addr
    except Exception:
        pass
    return arp


def is_samsung_mac(mac):
    prefix = mac[:8].lower()
    return prefix in SAMSUNG_OUI


def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "unknown"


def guess_device_type(hostname, mac):
    h = hostname.lower()
    if any(k in h for k in ["tv", "tizen", "smart-tv"]):
        return "TV  Smart TV"
    if any(k in h for k in ["phone", "galaxy", "sm-", "android"]):
        return "PHN Galaxy Phone/Tablet"
    if any(k in h for k in ["printer", "scx", "clx", "sl-"]):
        return "PRT Printer"
    if any(k in h for k in ["fridge", "ref", "washer", "ac", "air"]):
        return "HOM Home Appliance"
    if any(k in h for k in ["watch", "gear"]):
        return "WCH Galaxy Watch"
    return "SAM Samsung Device"


def scan_network(network_range):
    """Scan a subnet for Samsung devices."""
    print(f"{DIM}  Subnet : {network_range}{RESET}\n")

    hosts = list(ipaddress.ip_network(network_range, strict=False).hosts())
    total = len(hosts)

    print(f"{YELLOW}  [{datetime.now().strftime('%H:%M:%S')}] Pinging {total} hosts...{RESET}")

    alive = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as pool:
        futures = {pool.submit(ping_host, str(h)): str(h) for h in hosts}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            ip = futures[future]
            if future.result():
                alive.append(ip)
            if done % 50 == 0:
                print(f"  {DIM}Progress: {done}/{total}...{RESET}", end="\r")

    print(f"  {GREEN}✓ Found {len(alive)} alive host(s){RESET}           ")

    arp = get_arp_table()

    samsung_devices = []
    for ip in alive:
        mac = arp.get(ip, "")
        if mac and is_samsung_mac(mac):
            hostname = get_hostname(ip)
            device_type = guess_device_type(hostname, mac)
            samsung_devices.append({
                "ip": ip,
                "mac": mac,
                "hostname": hostname,
                "type": device_type,
            })

    return samsung_devices


def print_results(devices):
    if not devices:
        print(f"\n{YELLOW}  No Samsung devices found.{RESET}")
        print(f"  {DIM}Tip: Make sure Samsung devices are ON and on the same network.{RESET}\n")
        return

    print(f"\n{GREEN}{BOLD}  Found {len(devices)} Samsung device(s):{RESET}\n")
    print(f"  {'IP Address':<18} {'MAC Address':<20} {'Type':<25} {'Hostname'}")
    print(f"  {'-'*18} {'-'*20} {'-'*25} {'-'*30}")

    for d in devices:
        print(
            f"  {GREEN}{d['ip']:<18}{RESET}"
            f" {CYAN}{d['mac']:<20}{RESET}"
            f" {d['type']:<25}"
            f" {DIM}{d['hostname']}{RESET}"
        )
    print()


def show_menu():
    """Interactive menu with all detected interfaces."""
    interfaces = get_all_interfaces()

    print(f"{BOLD}  Select scan mode:{RESET}\n")
    options = []
    idx = 1

    # Show all detected network interfaces
    for iface in interfaces:
        print(f"  {CYAN}[{idx}]{RESET} {iface['name']}")
        print(f"      {DIM}→ {iface['subnet']}  (your IP: {iface['ip']}){RESET}")
        options.append(("iface", iface['subnet']))
        idx += 1

    # Custom range
    print(f"\n  {CYAN}[{idx}]{RESET} Custom IP range")
    print(f"      {DIM}→ Enter any subnet manually{RESET}")
    options.append(("custom", None))
    idx += 1

    # Multiple ranges
    print(f"\n  {CYAN}[{idx}]{RESET} Scan multiple ranges at once")
    options.append(("multi", None))

    print()
    while True:
        try:
            choice = input(f"  {BOLD}Enter choice [1-{idx}]: {RESET}").strip()
            c = int(choice)
            if 1 <= c <= idx:
                break
            print(f"  {RED}Please enter a number between 1 and {idx}{RESET}")
        except (ValueError, KeyboardInterrupt):
            print(f"\n  {YELLOW}Exiting.{RESET}\n")
            input("  Press Enter to close...")
            sys.exit(0)

    mode, preset_range = options[c - 1]

    if mode == "custom":
        preset_range = input(f"  {BOLD}Enter subnet (e.g. 192.168.1.0/24): {RESET}").strip()
        return [preset_range]

    if mode == "multi":
        raw = input(f"  {BOLD}Enter subnets separated by commas: {RESET}").strip()
        return [r.strip() for r in raw.split(",") if r.strip()]

    return [preset_range]


def main():
    banner()

    # Check if running as admin
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print(f"{YELLOW}  [!] Tip: Run as Administrator for best ARP results.{RESET}\n")
    except Exception:
        pass

    # Non-interactive CLI mode
    if len(sys.argv) > 1:
        ranges = sys.argv[1:]
    else:
        ranges = show_menu()

    all_devices = []
    total_start = time.time()

    for network_range in ranges:
        print(f"\n{BOLD}  Scanning {network_range}...{RESET}\n")
        start = time.time()
        devices = scan_network(network_range)
        elapsed = time.time() - start
        all_devices.extend(devices)
        print(f"  {DIM}Range done in {elapsed:.1f}s{RESET}")

    print_results(all_devices)
    total_elapsed = time.time() - total_start
    print(f"  {DIM}Total scan time: {total_elapsed:.1f}s{RESET}\n")
    input("  Press Enter to exit...")


if __name__ == "__main__":
    main()
