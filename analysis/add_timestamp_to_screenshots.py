import binascii
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
from glob import glob
from os.path import basename, join, expanduser, isfile, dirname

FONT_SIZE = 48
FONT_PATH = expanduser(
    "~/dev/dark-patterns/data/b612-master/TTF/B612 Mono-Italic.ttf")
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)

# file containing X, Y of all detected timers
TIMER_COORDINATES_CSV = "/home/gacar/dev/dark-patterns/data/timer_coords.csv"
TIMER_MARK_X_OFFSET = 20


def load_coordinates(timer_coords_csv=TIMER_COORDINATES_CSV):
    timer_coords = {}
    for l in open(timer_coords_csv):
        _, top, left, url = l.rstrip().split("\t")
        checksum = hex(binascii.crc32(url)).split('x')[-1]
        timer_coords[checksum] = (int(left), int(top))
    return timer_coords


def add_text_to_png(png_path, text, timer_coords=None):
    image = Image.open(png_path)
    w, h = image.size
    img_draw = ImageDraw.Draw(
        image  # Image
    )
    mark_x = w/2 - 250
    img_draw.rectangle((mark_x, h-80, mark_x+500, h-25), outline='red', fill='gray')
    img_draw.text((mark_x+10, h-75), text, (255, 255, 255), font=FONT)
    if timer_coords:
        url_checksum = basename(dirname(png_path)).split('_')[-1]
        x, y = timer_coords.get(url_checksum, (0, 0))
        if x:
            img_draw.ellipse(
                [(x-TIMER_MARK_X_OFFSET, y),
                 (x, y+TIMER_MARK_X_OFFSET)], fill=(255, 0, 0, 200),
                outline='blue')
        else:
            print "Cannot find", url_checksum
    return image


def add_date_text_to_images(search_pattern, out_dir=None, timer_coords=None):
    for png_path in glob(search_pattern):
        png_name = basename(png_path)
        if out_dir is None:
            out_png_path = png_path.replace(".png", "_marked.png")
        else:
            out_png_path = join(out_dir, png_name)
        if isfile(out_png_path):
            print ("Already marked, skipping %s" % out_png_path)
            continue
        date_str = png_name.split("_")[1]
        human_date_str = datetime.strptime(
            date_str, "%Y%m%d-%H%M%S").strftime("%b %d %H:%M:%S")
        new_image = add_text_to_png(png_path, human_date_str, timer_coords)
        new_image.save(out_png_path)


if __name__ == '__main__':
    timer_coords = load_coordinates(TIMER_COORDINATES_CSV)
    screenshots_pattern = expanduser("~/stateful_countdown_crawl_*/output/*/*.png")
    add_date_text_to_images(screenshots_pattern, None, timer_coords)
