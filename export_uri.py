import sys
import json
import base64

# از منطق پارس موجود استفاده می‌کنیم تا از تکرار جلوگیری شود
from print import parse_wg_config


def build_wireguard_uri(config_json: dict) -> str:
    """
    یک URI با طرح wireguard می‌سازد که محتوای آن JSON کدگذاری‌شده با base64 است.
    خروجی به شکل "wireguard://<base64(JSON)>" خواهد بود.
    """
    # JSON فشرده برای کوتاه‌تر شدن URI
    json_compact = json.dumps(config_json, ensure_ascii=False, separators=(",", ":"))
    encoded = base64.b64encode(json_compact.encode("utf-8")).decode("ascii")
    return f"wireguard://{encoded}"


def main():
    # ورودی: مسیر فایل کانفیگ WireGuard مانند wg.conf
    if len(sys.argv) < 2:
        print("Usage: python export_uri.py <config-file>")
        sys.exit(1)

    input_path = sys.argv[1]

    # خواندن محتوای فایل کانفیگ
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # تولید JSON ساخت‌یافته براساس پارسر موجود
    config_json = parse_wg_config(text)

    # چاپ JSON خوانا برای بررسی کاربر
    print(json.dumps(config_json, ensure_ascii=False, indent=2))

    # تولید و چاپ URI بر پایه base64 برای ایمپورت سریع
    uri = build_wireguard_uri(config_json)
    print("\nURI:")
    print(uri)


if __name__ == "__main__":
    main()


