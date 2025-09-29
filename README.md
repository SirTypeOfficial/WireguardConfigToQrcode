# WireGuard Config To QR Code / تبدیل کانفیگ وایرگارد به QR


## 🇮🇷 فارسی

این مخزن مجموعه‌ای از اسکریپت‌های پایتون برای کار با کانفیگ‌های WireGuard است؛ شامل تبدیل به QR (PNG/SVG)، ساخت JSON سازگار با sing-box/Throne، ساخت URI و لینک‌های SN، و کپی سریع بخش `outbound` به کلیپ‌بورد.

- ساختار پروژه
  - `main.py`: تولید QR از متن کانفیگ و ذخیره خروجی‌ها به صورت PNG و SVG.
  - `export_config.py`: خواندن `wg.conf` و تولید JSON ساخت‌یافته مطابق الگوی شبکه (DNS، inbounds/outbounds، route...).
  - `wg2throne.py`: پارس فایل WireGuard و تولید آبجکت‌های JSON سازگار با sing-box/Throne (endpoint/outbound و آرایه outbounds).
  - `copy_outbound.py`: استخراج تنها بخش `outbound` از خروجی `wg2throne` و کپی به کلیپ‌بورد (Windows).
  - `print.py`: پارسر سبک برای `wg.conf` و تبدیل آن به یک JSON حداقلی (کلیدهای اصلی WireGuard).
  - `export_uri.py`: ساخت `wireguard://<base64(JSON-compact)>` برای ایمپورت سریع.
  - `export_sn.py`: ساخت لینک `sn://wg?<payload>` با فشرده‌سازی zlib و base64url بدون پدینگ.
  - `wg.conf`: فایل نمونه ورودی WireGuard (می‌توانید مسیر دلخواه بدهید).

- پیش‌نیازها
  - Python 3.8+
  - نصب پکیج‌ها:
    ```bash
    pip install qrcode[pil]
    ```

- استفاده سریع
  - تولید QR از فایل کانفیگ:
    ```bash
    python main.py path/to/wg.conf [output-basename]
    # یا خواندن از stdin
    type path\to\wg.conf | python main.py - myqr
    ```
  - تولید JSON کامل از `wg.conf`:
    ```bash
    python export_config.py [path/to/wg.conf]
    ```
  - تولید آبجکت‌های Throne/sing-box:
    ```bash
    python wg2throne.py path/to/wg.conf
    ```
  - کپی `outbound` به کلیپ‌بورد (Windows):
    ```bash
    python copy_outbound.py [path/to/wg.conf]
    ```
  - ساخت URI واردکردنی WireGuard:
    ```bash
    python export_uri.py path/to/wg.conf
    ```
  - ساخت لینک SN فشرده:
    ```bash
    python export_sn.py path/to/wg.conf
    ```

- جزئیات ماژول‌ها
  - `main.py`
    - تابع `generate_qr(config_text, output_base)`: تولید PNG و SVG.
    - ورودی می‌تواند فایل یا stdin باشد (`-`).
  - `export_config.py`
    - `_parse_wg_conf`: پارس سکشن‌های `[Interface]` و `[Peer]`.
    - `_split_endpoint`: تبدیل `host:port` به `(host, port)`.
    - `build_config_from_wg`: ساخت ساختار کامل JSON (dns/inbounds/outbounds/route) از `wg.conf`.
    - `main`: خواندن مسیر ورودی و چاپ JSON.
  - `wg2throne.py`
    - `build_from_text`: خروجی آبجکت `endpoint`، `outbound` و `outbounds_array` سازگار با Throne.
  - `copy_outbound.py`
    - `build_outbound_json_from_conf`: فقط بخش `outbound` را تولید می‌کند و با `clip` در ویندوز کپی می‌کند.
  - `print.py`
    - `parse_wg_config`: پارس حداقلی برای کلیدهای WireGuard (PrivateKey, Address, DNS, MTU, PublicKey, AllowedIPs, Endpoint).
  - `export_uri.py`
    - `build_wireguard_uri`: تولید `wireguard://` با JSON فشرده و base64.
  - `export_sn.py`
    - `build_sn_link`: تولید `sn://wg?` با zlib + base64url بدون پدینگ.

- نکات
  - تمام اسکریپت‌ها از UTF-8 استفاده می‌کنند.
  - اگر `wg.conf` در کنار اسکریپت نباشد می‌توانید مسیر دلخواه را بدهید.
  - برای ویندوز، کپی کلیپ‌بورد با ابزار داخلی `clip` انجام می‌شود.


## 🇬🇧 English

This repository provides Python scripts to work with WireGuard configs: generate QR (PNG/SVG), produce sing-box/Throne-compatible JSON, create importable URIs and SN links, and quickly copy the `outbound` section to clipboard.

- Project Structure
  - `main.py`: Generate QR codes from config text and save PNG/SVG outputs.
  - `export_config.py`: Read `wg.conf` and build a structured JSON (DNS, inbounds/outbounds, route...).
  - `wg2throne.py`: Parse WireGuard config and produce sing-box/Throne-compatible JSON objects (endpoint/outbound and outbounds array).
  - `copy_outbound.py`: Extract only the `outbound` section from `wg2throne` output and copy to clipboard (Windows).
  - `print.py`: Lightweight parser for `wg.conf` to a minimal WireGuard JSON.
  - `export_uri.py`: Build `wireguard://<base64(JSON-compact)>` for quick import.
  - `export_sn.py`: Build `sn://wg?<payload>` using zlib compression and base64url without padding.
  - `wg.conf`: Example WireGuard input file (you can pass any path).

- Prerequisites
  - Python 3.8+
  - Install dependencies:
    ```bash
    pip install qrcode[pil]
    ```

- Quick Usage
  - Generate QR from config file:
    ```bash
    python main.py path/to/wg.conf [output-basename]
    # Or from stdin
    type path\to\wg.conf | python main.py - myqr
    ```
  - Produce full JSON from `wg.conf`:
    ```bash
    python export_config.py [path/to/wg.conf]
    ```
  - Generate Throne/sing-box objects:
    ```bash
    python wg2throne.py path/to/wg.conf
    ```
  - Copy `outbound` to clipboard (Windows):
    ```bash
    python copy_outbound.py [path/to/wg.conf]
    ```
  - Build importable WireGuard URI:
    ```bash
    python export_uri.py path/to/wg.conf
    ```
  - Build compressed SN link:
    ```bash
    python export_sn.py path/to/wg.conf
    ```

- Module Details
  - `main.py`
    - `generate_qr(config_text, output_base)`: emits PNG and SVG files.
    - Input can be a file or stdin (`-`).
  - `export_config.py`
    - `_parse_wg_conf`: parse `[Interface]` and `[Peer]` sections.
    - `_split_endpoint`: convert `host:port` to `(host, port)`.
    - `build_config_from_wg`: construct full JSON (dns/inbounds/outbounds/route) from `wg.conf`.
    - `main`: read input path and print JSON.
  - `wg2throne.py`
    - `build_from_text`: outputs `endpoint`, `outbound`, and `outbounds_array` for Throne.
  - `copy_outbound.py`
    - `build_outbound_json_from_conf`: produces only the `outbound` section and copies with `clip` on Windows.
  - `print.py`
    - `parse_wg_config`: minimal WireGuard keys parser (PrivateKey, Address, DNS, MTU, PublicKey, AllowedIPs, Endpoint).
  - `export_uri.py`
    - `build_wireguard_uri`: produce `wireguard://` with compact JSON and base64.
  - `export_sn.py`
    - `build_sn_link`: produce `sn://wg?` using zlib + base64url without padding.

- Notes
  - All scripts use UTF-8.
  - If `wg.conf` is not beside the script, provide the desired path.
  - On Windows, clipboard copy uses the built-in `clip` utility.
