import sys
import json
import zlib
import base64

# از پارسر موجود استفاده می‌کنیم تا ساختار پروژه حفظ شود
from print import parse_wg_config


def to_base64url_no_pad(data: bytes) -> str:
    """
    تبدیل بایت‌ها به Base64-URL بدون پدینگ '='.
    """
    b64 = base64.urlsafe_b64encode(data).decode("ascii")
    return b64.rstrip("=")


def build_sn_link(config_json: dict) -> str:
    """
    لینک SN برمی‌گرداند به صورت:
    sn://wg?<payload>
    که payload برابر است با zlib-deflate(JSON فشرده) سپس base64url (بدون پدینگ).
    """
    # JSON فشرده برای کوتاه‌تر شدن
    json_compact = json.dumps(config_json, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    # فشرده‌سازی با zlib (سطح پیش‌فرض)
    compressed = zlib.compress(json_compact)

    # base64url بدون پدینگ
    payload = to_base64url_no_pad(compressed)

    return f"sn://wg?{payload}"


def main():
    # ورودی: مسیر فایل کانفیگ WireGuard مانند wg.conf
    if len(sys.argv) < 2:
        print("Usage: python export_sn.py <config-file>")
        sys.exit(1)

    input_path = sys.argv[1]

    # خواندن محتوای فایل کانفیگ
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # تولید JSON ساخت‌یافته براساس پارسر موجود
    config_json = parse_wg_config(text)

    # چاپ لینک SN برای ایمپورت سریع‌تر
    link = build_sn_link(config_json)
    print(link)


if __name__ == "__main__":
    main()


