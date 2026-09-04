#!/usr/bin/env python3
"""
add_ip_network.py

Fetches the machine's current public IPv4 (via ifconfig.me), computes its
/16 network and appends it to a file if that exact line doesn't already exist.
duplicate lines.

Usage:
    python3 add_ip_network.py                    # appends to ./au.zone, /16, IPv4
    python3 add_ip_network.py --file custom.zone
    python3 add_ip_network.py --prefix 24
    python3 add_ip_network.py --ipv6 --prefix 32  # fetch/compute IPv6 instead
"""
import argparse
import ipaddress
import subprocess
import sys

IFCONFIG_URL = "https://ifconfig.me/ip"


def fetch_public_ip(ipv6: bool) -> str:
    # urllib has no way to force IPv4 vs IPv6 at the socket level, so on a
    # dual-stack machine it follows whatever the OS resolver prefers —
    # which can silently hand back the wrong family. Shelling out to curl
    # with -4/-6 forces the family explicitly, same as the original bash
    # command this script is meant to replace.
    flag = "-6" if ipv6 else "-4"
    try:
        ip = subprocess.run(
            ["curl", flag, "-s", "--max-time", "10", IFCONFIG_URL],
            capture_output=True, text=True, check=True, timeout=15,
        ).stdout.strip()
    except FileNotFoundError:
        raise RuntimeError("curl not found — install it, or use --ip to skip fetching")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"curl failed: {e.stderr.strip() or e}")
 
    if not ip:
        raise RuntimeError(f"No {'IPv6' if ipv6 else 'IPv4'} address returned — "
                            f"do you have {'IPv6' if ipv6 else 'IPv4'} connectivity?")
 
    addr = ipaddress.ip_address(ip)
    if ipv6 and addr.version != 6:
        raise RuntimeError(f"Expected an IPv6 address but got {ip}")
    if not ipv6 and addr.version != 4:
        raise RuntimeError(f"Expected an IPv4 address but got {ip}")
    return ip


def append_if_new(path: str, line: str) -> bool:
    """Returns True if the line was added, False if it was already present."""
    existing = set()
    try:
        with open(path) as f:
            existing = {l.strip() for l in f if l.strip()}
    except FileNotFoundError:
        pass  # file will be created below

    if line in existing:
        return False

    with open(path, "a") as f:
        f.write(line + "\n")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="ipset/ipset.zone", help="file to append to (default: ipset/ipset.zone)")
    ap.add_argument("--prefix", type=int, default=16, help="network prefix length (default: 16)")
    ap.add_argument("--ipv6", action="store_true", help="fetch/compute IPv6 instead of IPv4")
    ap.add_argument("--ip", help="use this IP directly instead of fetching from ifconfig.me")
    args = ap.parse_args()

    try:
        ip = args.ip or fetch_public_ip(args.ipv6)
        network = ipaddress.ip_network(f"{ip}/{args.prefix}", strict=False)
    except (RuntimeError, ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    line = str(network)
    if append_if_new(args.file, line):
        print(f"Added {line} to {args.file}")
    else:
        print(f"{line} already present in {args.file} — skipped")


if __name__ == "__main__":
    main()