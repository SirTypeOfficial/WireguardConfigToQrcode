#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
کپی فقط بخش outbound از خروجی ماژول wg2throne به کلیپ‌بورد و چاپ در خروجی استاندارد.
نحوه اجرا:
    python copy_outbound.py [مسیر_فایل_wg.conf]
اگر مسیر ندهید، به صورت پیش‌فرض فایل wg.conf کنار اسکریپت خوانده می‌شود.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Optional

import wg2throne


def read_text_file(file_path: Path) -> str:
    """متن فایل ورودی را با انکودینگ UTF-8 می‌خواند."""
    return file_path.read_text(encoding="utf-8")


def build_outbound_json_from_conf(conf_text: str) -> str:
    """خروجی outbound را از متن کانفیگ WireGuard استخراج و به JSON فرمت‌شده تبدیل می‌کند."""
    result = wg2throne.build_from_text(conf_text, tag="wg-1")
    outbound_obj = result.get("outbound", {})
    return json.dumps(outbound_obj, indent=2, ensure_ascii=False)


def copy_to_clipboard(text: str) -> None:
    """متن را در کلیپ‌بورد سیستم کپی می‌کند (در ویندوز از clip استفاده می‌شود)."""
    # توجه: کاربر در ویندوز است؛ بنابراین از ابزار clip استفاده می‌کنیم.
    try:
        subprocess.run(["clip"], input=text, text=True, check=True)
    except Exception:
        # اگر به هر دلیل clip در دسترس نبود، بدون خطا دادن ادامه می‌دهیم.
        pass


def main(argv: Optional[list] = None) -> int:
    """تابع اصلی اجرا: خواندن فایل، تبدیل outbound به JSON، کپی به کلیپ‌بورد و چاپ."""
    args = argv if argv is not None else sys.argv[1:]

    # تعیین مسیر فایل کانفیگ؛ پیش‌فرض: wg.conf در همین پوشه
    conf_path = Path(args[0]) if args else Path(__file__).with_name("wg.conf")
    if not conf_path.exists():
        print(f"فایل کانفیگ یافت نشد: {conf_path}")
        return 1

    # خواندن کانفیگ و ساخت JSON بخش outbound
    conf_text = read_text_file(conf_path)
    outbound_json = build_outbound_json_from_conf(conf_text)

    # کپی در کلیپ‌بورد
    copy_to_clipboard(outbound_json)

    # چاپ برای مشاهده سریع
    print(outbound_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())


