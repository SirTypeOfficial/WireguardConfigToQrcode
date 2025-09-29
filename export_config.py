import json
import os
import re
from typing import Dict, Any, List, Tuple


def _parse_wg_conf(conf_path: str) -> Dict[str, Dict[str, str]]:
    """
    پارس ساده فایل WireGuard به ساختار دیکشنری بر اساس سکشن‌ها [Interface] و [Peer].
    خروجی به صورت {"Interface": {...}, "Peer": {...}}
    """
    if not os.path.exists(conf_path):
        raise FileNotFoundError(f"فایل یافت نشد: {conf_path}")

    sections: Dict[str, Dict[str, str]] = {}
    current: str = ""

    key_val_pattern = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*(.+?)\s*$")

    with open(conf_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#") or line.startswith(";"):
                # خط کامنت
                continue
            if line.startswith("[") and line.endswith("]"):
                # شروع یک سکشن جدید
                current = line.strip("[]").strip()
                if current not in sections:
                    sections[current] = {}
                continue
            m = key_val_pattern.match(line)
            if m and current:
                key, value = m.group(1), m.group(2)
                sections[current][key] = value

    return sections


def _split_endpoint(endpoint: str) -> Tuple[str, int]:
    """
    تبدیل مقدار Endpoint به (host, port)
    مثال: big.example.com:1234 -> (big.example.com, 1234)
    """
    if not endpoint:
        raise ValueError("Endpoint خالی است.")
    if ":" not in endpoint:
        raise ValueError("فرمت Endpoint نامعتبر است. انتظار host:port می‌رود.")
    host, port_str = endpoint.rsplit(":", 1)
    port = int(port_str)
    return host, port


def _parse_ip_list(value: str) -> List[str]:
    """
    تبدیل رشته‌ای مانند "1.1.1.1, 1.0.0.1" به لیست آیتم‌ها
    """
    return [item.strip() for item in value.split(",") if item.strip()]


def build_config_from_wg(conf_path: str) -> Dict[str, Any]:
    """
    بر اساس فایل wg.conf، خروجی JSON مطابق قالب درخواستی می‌سازد.
    نکته‌ها:
    - آدرس DNS اول برای هر دو ورودی DoH و مستقیم استفاده می‌شود (مطابق نمونه خروجی).
    - دامنه بخش Endpoint در قانون DNS قرار می‌گیرد.
    - سایر فیلدها از فایل خوانده می‌شوند و در قالب ثابت تزریق می‌گردند.
    """
    sections = _parse_wg_conf(conf_path)

    interface = sections.get("Interface", {})
    peer = sections.get("Peer", {})

    private_key = interface.get("PrivateKey", "")
    address = interface.get("Address", "")
    mtu = interface.get("MTU", "")
    dns_raw = interface.get("DNS", "")
    dns_list = _parse_ip_list(dns_raw) if dns_raw else []
    primary_dns = dns_list[0] if dns_list else "1.1.1.1"

    public_key = peer.get("PublicKey", "")
    endpoint = peer.get("Endpoint", "")
    host, port = _split_endpoint(endpoint) if endpoint else ("", 0)

    config: Dict[str, Any] = {
        "dns": {
            "independent_cache": True,
            "rules": [
                {
                    "domain": [host] if host else [],
                    "server": "dns-direct",
                }
            ],
            "servers": [
                {
                    "address": f"https://{primary_dns}/dns-query",
                    "address_resolver": "dns-direct",
                    "strategy": "ipv4_only",
                    "tag": "dns-remote",
                },
                {
                    "address": primary_dns,
                    "address_resolver": "dns-local",
                    "detour": "direct",
                    "strategy": "ipv4_only",
                    "tag": "dns-direct",
                },
                {
                    "address": "local",
                    "detour": "direct",
                    "tag": "dns-local",
                },
                {
                    "address": "rcode://success",
                    "tag": "dns-block",
                },
            ],
        },
        "experimental": {
            "clash_api": {
                "cache_file": "../cache/clash.db",
                "external_controller": "127.0.0.1:9090",
                "external_ui": "../files/yacd",
            }
        },
        "inbounds": [
            {
                "listen": "0.0.0.0",
                "listen_port": 6450,
                "override_address": "8.8.8.8",
                "override_port": 53,
                "tag": "dns-in",
                "type": "direct",
            },
            {
                "domain_strategy": "",
                "endpoint_independent_nat": True,
                "inet4_address": [address] if address else [],
                "mtu": int(mtu) if str(mtu).isdigit() else 1500,
                "sniff": True,
                "sniff_override_destination": False,
                "stack": "mixed",
                "tag": "tun-in",
                "type": "tun",
            },
            {
                "domain_strategy": "",
                "listen": "0.0.0.0",
                "listen_port": 2080,
                "sniff": True,
                "sniff_override_destination": False,
                "tag": "mixed-in",
                "type": "mixed",
            },
        ],
        "log": {"level": "panic"},
        "outbounds": [
            {
                "local_address": [address] if address else [],
                "mtu": int(mtu) if str(mtu).isdigit() else 1320,
                "peer_public_key": public_key,
                "pre_shared_key": "",
                "private_key": private_key,
                "server": host,
                "server_port": port,
                "type": "wireguard",
                "domain_strategy": "",
                "tag": "proxy",
            },
            {"tag": "direct", "type": "direct"},
            {"tag": "bypass", "type": "direct"},
            {"tag": "block", "type": "block"},
            {"tag": "dns-out", "type": "dns"},
        ],
        "route": {
            "auto_detect_interface": True,
            "rules": [
                {"outbound": "dns-out", "port": [53]},
                {"inbound": ["dns-in"], "outbound": "dns-out"},
                {"geoip": ["ir"], "outbound": "bypass"},
                {
                    "ip_cidr": ["224.0.0.0/3", "ff00::/8"],
                    "outbound": "block",
                    "source_ip_cidr": ["224.0.0.0/3", "ff00::/8"],
                },
            ],
        },
    }

    return config


def main() -> None:
    """
    اجرای خط فرمان: فایل wg.conf در همین پوشه را خوانده و JSON را در stdout چاپ می‌کند.
    استفاده: python export_config.py [مسیر-دلخواه-به-wg.conf]
    """
    import sys

    conf_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "wg.conf")
    config = build_config_from_wg(conf_path)
    # چاپ JSON با اینکدینگ استاندارد
    print(json.dumps(config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


