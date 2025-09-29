import sys
import json
import re

def parse_wg_config(text: str):
    data = {
        "type": "wireguard",
        "server": "",
        "server_port": 0,
        "private_key": "",
        "public_key": "",
        "address": [],
        "dns": [],
        "mtu": None,
        "allowed_ips": []
    }

    # [Interface]
    priv = re.search(r"PrivateKey\s*=\s*(.+)", text)
    addr = re.search(r"Address\s*=\s*(.+)", text)
    dns = re.search(r"DNS\s*=\s*(.+)", text)
    mtu = re.search(r"MTU\s*=\s*(\d+)", text)

    if priv: data["private_key"] = priv.group(1).strip()
    if addr: data["address"] = [a.strip() for a in addr.group(1).split(",")]
    if dns: data["dns"] = [d.strip() for d in dns.group(1).split(",")]
    if mtu: data["mtu"] = int(mtu.group(1))

    # [Peer]
    pub = re.search(r"PublicKey\s*=\s*(.+)", text)
    allowed = re.search(r"AllowedIPs\s*=\s*(.+)", text)
    endpoint = re.search(r"Endpoint\s*=\s*(.+)", text)

    if pub: data["public_key"] = pub.group(1).strip()
    if allowed: data["allowed_ips"] = [a.strip() for a in allowed.group(1).split(",")]
    if endpoint:
        host, port = endpoint.group(1).rsplit(":", 1)
        data["server"] = host.strip()
        data["server_port"] = int(port.strip())

    return data


def main():
    if len(sys.argv) < 2:
        print("Usage: python wg2json.py <config-file>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    config_json = parse_wg_config(text)
    print(json.dumps(config_json, indent=2))


if __name__ == "__main__":
    main()
