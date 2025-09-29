import sys
import qrcode
import qrcode.image.svg

def generate_qr(config_text: str, output_base: str = "qrcode"):
    # PNG خروجی
    img = qrcode.make(config_text)
    png_path = f"{output_base}.png"
    img.save(png_path)
    print(f"[+] PNG saved as {png_path}")

    # SVG خروجی
    factory = qrcode.image.svg.SvgImage
    img_svg = qrcode.make(config_text, image_factory=factory)
    svg_path = f"{output_base}.svg"
    with open(svg_path, "wb") as f:
        img_svg.save(f)
    print(f"[+] SVG saved as {svg_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python wg_qr.py <config-file> [output-basename]")
        print("Or:    echo '<config>' | python wg_qr.py - [output-basename]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_base = sys.argv[2] if len(sys.argv) > 2 else "qrcode"

    if input_path == "-":
        config_text = sys.stdin.read()
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            config_text = f.read()

    if not config_text.strip():
        print("Error: config is empty!")
        sys.exit(2)

    generate_qr(config_text, output_base)


if __name__ == "__main__":
    main()
