from __future__ import print_function
from beautifultable import BeautifulTable
from tqdm import tqdm
from urlparse import urlparse
import json
import os.path
import pandas as pd
import readchar
import sqlite3
import sys
import unicodedata

usage = 'Usage: python %s CLUSTERS-FILE DATABASE START' % __file__
help_message = '''Tool for viewing clusters described in a file. CLUSTERS-FILE should be
a file in the following pseudo-JSON format:

{"cluster_id": [{"id": 1562, "caps": true, "popup": false, "x": "middle", "y": "top"}, ...]}
...

So each entry is one cluster, and it lists the segments that belong to that cluster.
cluster_ids are the integer labels assigned by the clustering algorithm, and each
segment has the attributes: id (integer index in the DATABASE), caps (boolean,
whether the text contains all-caps words), popup (boolean, whether the segment was
in a popup), x (location - "left", "middle", or "right"), and y (location "top", "middle",
or "bottom"). Each line should be one entry.

START is the index (from 1) of the line to start at.'''

def save(save_list, save_file):
    with open(save_file, 'a') as f:
        for s in save_list:
            f.write(str(s) + '\n')

def clear_screen():
    print('\033c')

def line_count(filename):
    with open(filename) as f:
        count = 0
        for _ in f:
            count = count + 1
    return count

if __name__ == '__main__':
    # Check usage
    if len(sys.argv[1:]) != 3:
        print(usage)
        print()
        print(help_message)
        sys.exit(1)

    clusters_file = sys.argv[1]
    db = sys.argv[2]
    start_index = int(sys.argv[3])

    reload(sys)
    sys.setdefaultencoding('utf-8')
    if not os.path.isfile(clusters_file):
        print('Error: Clusters file not found: %s' % clusters_file)
        sys.exit(1)
    if not os.path.isfile(db):
        print('Error: Database not found: %s' % db)
        sys.exit(1)

    # Read clusters
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    total_clusters = line_count(clusters_file)
    save_list = []
    save_file = 'saved_clusters.txt'
    with open(clusters_file, 'r') as f:
        i = 1
        for line in f:
            if i < start_index:
                i = i + 1
                continue

            clear_screen()

            cluster_json = json.loads(line)
            cluster = cluster_json[cluster_json.keys()[0]]
            nsegments = len(cluster)
            print('CLUSTER LINE %d/%d (%d segments)' % (i, total_clusters, nsegments))

            # Read text of each segment from db
            print('Reading segments from database...')
            subset_size = 50
            cluster = cluster[:min(nsegments, subset_size)] # trim number of segments to display
            seg_ids = '(' + ', '.join([str(seg['id']) for seg in cluster]) + ')'
            query = '''select sg.inner_text, sv.site_url from
                segments as sg join site_visits as sv on sg.visit_id = sv.visit_id
                where sg.id in ''' + seg_ids
            cur = con.cursor()
            j = 0
            for seg in tqdm(cur.execute(query)):
                cluster[j]['domain'] = urlparse(seg['site_url']).netloc
                cluster[j]['inner_text'] = seg['inner_text']
                j = j + 1

            # Make table
            print('Constructing table of segments...')
            table = BeautifulTable()
            table.column_headers = ['segment id', 'domain', 'inner_text', 'caps', 'popup', 'x', 'y']
            for seg in tqdm(cluster):
                inner_text = unicodedata.normalize('NFKD', seg['inner_text']).encode('ascii', 'ignore').encode('string_escape')
                table.append_row([seg['id'], seg['domain'], inner_text, seg['caps'], seg['popup'], seg['x'], seg['y']])
            print(table)
            print('%d segments, %d shown' % (nsegments, min(nsegments, subset_size)))

            # Wait for command
            key = ''
            while key != 'n' and key != 's' and key != 'q':
                print('\nEnter command:')
                print('n: switch to next cluster')
                print('s: save current cluster')
                print('q: save to file and quit')
                print('> ', end='')
                sys.stdout.flush()
                key = readchar.readchar().lower()
                print()
            if key == 'n':
                pass
            elif key == 's':
                save_list.append(i)
            else:
                break

            # Save
            if i % 20 == 0:
                save(save_list, save_file)
                save_list = []

            i = i + 1

    save(save_list, save_file)
    print('Ended at line %i' % i)
