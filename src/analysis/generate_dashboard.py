import argparse
import pandas
import os
import sqlite3
import pandas as pd
from jinja2 import Template
from urlparse import urlparse
from datetime import datetime
from PIL import Image
import base64
import cStringIO

screenshots = {}

def sortfn(a, b):
    idx1 = int(a.split('_')[3])
    idx2 = int(b.split('_')[3])
    if idx1 < idx2:
        return -1
    elif idx1 == idx2:
        return 0
    else:
        return 1

def get_segment_images(screenshots_dir, row):
    ts = row['time_stamp'].split('.')[0]
    ts = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

    files = screenshots[urlparse(row['site_url']).netloc]

    current_file = files[0]
    for f in files:
        fts = datetime.strptime(f.split('_')[2], "%Y-%m-%dT%H:%M:%S")

        if ts < fts:
            current_file = f
            break

    img_path = os.path.join(screenshots_dir, current_file)
    img = Image.open(img_path)
    img = img.crop((row['left'], row['top'], row['left'] + row['width'], row['top'] + row['height']))

    try:
        buffer = cStringIO.StringIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue())
    except:
        return ("data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==", img_path)

    return ("data:image/png;base64, " + img_str, img_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a clustering dashboard')
    parser.add_argument('screenshots_dir', help='Folder containing the screenshots')
    parser.add_argument('cluster_output_file', help='File containing the clustering output')
    parser.add_argument('template', help='Template to generate the dashboard output')
    parser.add_argument('output', help='Name of the dashboard HTML output file')

    args = parser.parse_args()

    screenshots_dir = args.screenshots_dir
    cluster_output_file = args.cluster_output_file
    template = args.template
    output = args.output

    print 'Listing the screenshot files...'
    screenshot_files = [filename for filename in os.listdir(screenshots_dir)]
    print 'Done.'

    print 'Grouping the screenshot files...'
    for sf in screenshot_files:
        splitsf = sf.split('_')

        if splitsf[1] in screenshots.keys():
            screenshots[splitsf[1]].append(sf)
        else:
            screenshots[splitsf[1]] = [sf]
    print 'Done.'

    print 'Sorting the screenshot files...'
    for key, value in screenshots.iteritems():
        screenshots[key] = sorted(screenshots[key], sortfn)
    print 'Done.'

    print 'Reading the clustering output file...'
    segs = pd.read_csv(cluster_output_file)
    print 'Done.'

    print 'Sorting the clusters...'
    segs.sort_values(by='cluster', inplace=True)
    print 'Done.'

    items = []

    for index, row in segs.iterrows():
        imgs = get_segment_images(screenshots_dir, row)
        items.append({'cluster_number': row['cluster'],
                      'url': row['site_url'].decode('utf-8'),
                      'text': row['inner_text'].decode('utf-8'),
                      'segment_screenshot': imgs[0],
                      'screenshot': imgs[1]})

    with open(template) as file_:
        template = Template(file_.read())

    template.stream(items = items).dump(output)
