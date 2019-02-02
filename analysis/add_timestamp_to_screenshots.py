from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
from glob import glob
from os.path import basename, join, expanduser

FONT_SIZE = 24
FONT_PATH = expanduser(
    "~/dev/dark-patterns/data/b612-master/TTF/B612 Mono-Italic.ttf")
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)


def add_text_to_png(png_path, text):
    image = Image.open(png_path)
    w, h = image.size
    ImageDraw.Draw(
        image  # Image
    ).text((w-250, h-40), text, (255, 119, 18), font=FONT)
    return image


def add_date_text_to_images(in_dir, out_dir):
    for png_path in glob(join(in_dir, "*.png")):
        png_name = basename(png_path)
        date_str = png_name.split("_")[1]
        human_date_str = datetime.strptime(
            date_str, "%Y%m%d-%H%M%S").strftime("%b %d %H:%M:%S")
        new_image = add_text_to_png(png_path, human_date_str)
        new_image.save(join(out_dir, png_name))


if __name__ == '__main__':
    img_dir = "/home/gacar/stateful_countdown_crawl/screenshots"
    add_date_text_to_images(img_dir, "/tmp/processed_imgs")
