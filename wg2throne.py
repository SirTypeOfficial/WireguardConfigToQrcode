#!/usr/bin/env python3
# wg2throne.py
# Parse a WireGuard .conf and print sing-box / Throne compatible JSON variants.
# Usage:
#   python wg2throne.py wg.conf
#   cat wg.conf | python wg2throne.py -

import sys, re, json, base64
from typing import List, Dict, Tuple, Optional

def split_sections(text: str):
    lines = text.splitlines()
    sections = []
    cur = None
    curname = None
    for ln in lines:
        ln_stripped = ln.strip()
        if not ln_stripped or ln_stripped.startswith('#') or ln_stripped.startswith(';'):
            continue
        m = re.match(r'^\s*\[(.+?)\]\s*$', ln)
        if m:
            if cur is not None:
                sections.append((curname, cur))
            curname = m.group(1)
            cur = {}
            continue
        if cur is None:
            continue
        m2 = re.match(r'^([^=]+?)\s*=\s*(.+)$', ln)
        if m2:
            k = m2.group(1).strip()
            v = m2.group(2).strip()
            cur[k] = v
    if cur is not None:
        sections.append((curname, cur))
    return sections

def parse_endpoint(endpoint: str):
    if not endpoint:
        return (None, None)
    endpoint = endpoint.strip()
    m = re.match(r'^\[([^\]]+)\]:(\d+)$', endpoint)
    if m:
        return (m.group(1), int(m.group(2)))
    if ':' in endpoint and endpoint.count(':')==1:
        host, port = endpoint.rsplit(':',1)
        try:
            return (host, int(port))
        except:
            return (host, None)
    return (endpoint, None)

def split_list_field(s: Optional[str]):
    if not s:
        return []
    return [p.strip() for p in s.split(',') if p.strip()]

def build_from_text(text: str, tag: str = "wg-1"):
    sections = split_sections(text)
    interface = None
    peers = []
    for name, kv in sections:
        if name.lower() == 'interface':
            interface = kv
        elif name.lower() == 'peer':
            peers.append(kv)
    if interface is None and not peers:
        raise ValueError("No [Interface] or [Peer] sections found.")
    interface = interface or {}

    private_key = interface.get('PrivateKey') or ""
    address_list = split_list_field(interface.get('Address') or "")
    dns_list = split_list_field(interface.get('DNS') or "")
    mtu = None
    if interface.get('MTU'):
        try:
            mtu = int(interface.get('MTU'))
        except:
            mtu = None

    parsed_peers = []
    for p in peers:
        pub = p.get('PublicKey') or ""
        allowed = split_list_field(p.get('AllowedIPs') or "")
        endpoint = p.get('Endpoint') or ""
        host, port = parse_endpoint(endpoint) if endpoint else (None, None)
        pk = p.get('PresharedKey') or p.get('PreSharedKey') or None
        keep = p.get('PersistentKeepalive') or None
        keep_int = None
        if keep:
            try:
                keep_int = int(keep)
            except:
                keep_int = None
        parsed_peers.append({
            'public_key': pub,
            'allowed_ips': allowed,
            'endpoint_host': host,
            'endpoint_port': port,
            'pre_shared_key': pk,
            'persistent_keepalive_interval': keep_int
        })

    endpoint_obj = {
        "type": "wireguard",
        "tag": f"{tag}-endpoint",
        "system": False,
        "name": "",
        "mtu": mtu or None,
        "address": address_list,
        "private_key": private_key,
        "listen_port": None,
        "peers": []
    }
    for pp in parsed_peers:
        endpoint_obj['peers'].append({
            "address": pp['endpoint_host'] or "",
            "port": pp['endpoint_port'] or None,
            "public_key": pp['public_key'] or "",
            "pre_shared_key": pp['pre_shared_key'] or "",
            "allowed_ips": pp['allowed_ips'] or [],
            "persistent_keepalive_interval": pp['persistent_keepalive_interval'] or 0,
            "reserved": [0,0,0]
        })

    outbound_obj = {
        "type": "wireguard",
        "tag": f"{tag}-outbound",
        "server": None,
        "server_port": None,
        "system_interface": False,
        "interface_name": "",
        "local_address": address_list,
        "private_key": private_key,
        "peers": []
    }
    if parsed_peers:
        first = parsed_peers[0]
        if first['endpoint_host']:
            outbound_obj['server'] = first['endpoint_host']
        if first['endpoint_port']:
            outbound_obj['server_port'] = first['endpoint_port']
    for pp in parsed_peers:
        outbound_obj['peers'].append({
            "server": pp['endpoint_host'] or "",
            "server_port": pp['endpoint_port'] or None,
            "public_key": pp['public_key'] or "",
            "pre_shared_key": pp['pre_shared_key'] or "",
            "allowed_ips": pp['allowed_ips'] or [],
            "reserved": [0,0,0]
        })

    outbounds_array = [outbound_obj]

    return {
        "raw": text,
        "base64": base64.b64encode(text.encode('utf-8')).decode('ascii'),
        "endpoint": endpoint_obj,
        "outbound": outbound_obj,
        "outbounds_array": outbounds_array,
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python wg2throne.py <wg.conf>")
        print("Or: cat wg.conf | python wg2throne.py -")
        sys.exit(1)
    path = sys.argv[1]
    if path == '-':
        text = sys.stdin.read()
    else:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    res = build_from_text(text, tag="wg-1")
    print("# ----- sing-box 'endpoint' object -----")
    print(json.dumps(res['endpoint'], indent=2, ensure_ascii=False))
    print("\n# ----- sing-box 'outbound' object -----")
    print(json.dumps(res['outbound'], indent=2, ensure_ascii=False))
    print("\n# ----- JSON array wrapper (paste this into Throne as outbounds) -----")
    print(json.dumps(res['outbounds_array'], indent=2, ensure_ascii=False))
    print("\n# ----- base64 of raw wg.conf (for alternative imports) -----")
    print(res['base64'])
    print("\n# ----- raw wg.conf -----")
    print(res['raw'])

if __name__ == '__main__':
    main()
