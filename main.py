import sys

from PIL import Image, ImageDraw, ImageFont


def write_text_on_png(text, png, location=None):
    # write text on the image at location
    img = Image.open(png)
    draw = ImageDraw.Draw(img)
    font_path = "arial.ttf"
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    text_colur = (255, 0, 0)  # red
    text_position = (50, 50)
    draw.text(text_position, text, font=font, fill=text_colur)
    img.save(f"{text}-certificate.png")
    return


def main():
    names = [
        "Paul K. Korir",
    ]
    template = "template.png"
    for name in names:
        write_text_on_png(name, template)

    return 0


if __name__ == '__main__':
    sys.exit(main())
