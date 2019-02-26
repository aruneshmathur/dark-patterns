import binascii
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
from glob import glob
from os.path import basename, join, expanduser, isfile, dirname
from _collections import defaultdict

FONT_SIZE = 36
SMALL_FONT_SIZE = 24
FONT_PATH = expanduser(
    "~/dev/dark-patterns/data/b612-master/TTF/B612 Mono-Italic.ttf")
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)
SMALL_FONT = ImageFont.truetype(FONT_PATH, SMALL_FONT_SIZE)

# file containing X, Y of all detected timers
TIMER_COORDINATES_CSV = expanduser(
    "~/dev/dark-patterns/analysis/timer-analysis/timer_coords.csv")
TIMER_MARK_X_OFFSET = 20


def load_coordinates(timer_coords_csv=TIMER_COORDINATES_CSV):
    timer_coords = defaultdict(set)
    for l in open(timer_coords_csv):
        _, top, left, url = l.rstrip().split("\t")
        checksum = hex(binascii.crc32(url)).split('x')[-1]
        timer_coords[checksum].add((int(left), int(top)))
    return timer_coords


def add_text_to_png(png_path, text, timer_coords=None):
    print("Will add mark to %s" % png_path)
    image = Image.open(png_path)
    w, h = image.size
    img_draw = ImageDraw.Draw(
        image
    )
    mark_x = w/2 - 250
    img_draw.rectangle((mark_x, h-90, mark_x+365, h-30), outline='red', fill='gray')
    site_url = basename(dirname(png_path))
    img_draw.text((mark_x+10, h-75), text, (255, 255, 255), font=FONT)
    img_draw.text((mark_x+10, h-30), site_url, (10, 10, 255), font=SMALL_FONT)

    if timer_coords:
        url_checksum = basename(dirname(png_path)).split('_')[-1]
        coord_pairs = timer_coords.get(url_checksum)
        if coord_pairs is None:
            print "Cannot find", url_checksum, png_path
        else:
            for (x, y) in coord_pairs:
                img_draw.ellipse(
                    [(x-TIMER_MARK_X_OFFSET, y),
                     (x, y+TIMER_MARK_X_OFFSET)], fill=(255, 0, 0, 200),
                    outline='blue')
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
