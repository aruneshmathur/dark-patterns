import sys
import os.path
import pandas as pd
from beautifultable import BeautifulTable, ALIGN_LEFT
import unicodedata
import readchar

RECORD_FILE = 'saved.txt'

def clear_screen():
    print '\033c'

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print 'Usage: python single_cluster_browser.py [cluster_file_pickle] [cluster_id_column]'
        sys.exit(1)

    reload(sys)
    sys.setdefaultencoding('utf-8')

    cluster_dataframe = None
    headers = None
    if not os.path.isfile(sys.argv[1]):
        print 'Error: Cluster pickle file not found.'
        sys.exit(1)
    else:
        cluster_dataframe = pd.read_pickle(sys.argv[1])
        headers = [sys.argv[2], 'hostname', 'inner_text']

    saved_clusters = []
    if os.path.isfile(RECORD_FILE):
        with open(RECORD_FILE, 'r') as f:
            # Read all the clusters completed so far
            for l in f.readlines():
                saved_clusters.append(l.strip())
    else:
        print 'Error: saved.txt file not found'
        sys.exit(2)

    to_view_clusters = cluster_dataframe[cluster_dataframe[sys.argv[2]].isin(saved_clusters)]
    to_view_clusters_ids = list(set(to_view_clusters[sys.argv[2]].tolist()))
    to_view_clusters_ids.sort(reverse = True)

    count = len(to_view_clusters_ids)
    i = 0

    while i < count:
        clear_screen()
        current_id = to_view_clusters_ids[i]
        current_cluster = to_view_clusters[to_view_clusters[sys.argv[2]] == current_id]

        table = BeautifulTable(max_width=160, default_alignment=ALIGN_LEFT)
        table.column_headers = headers

        for index, row in current_cluster.iterrows():
            table.append_row([row[sys.argv[2]], row['hostname'], unicodedata.normalize('NFKD', row['inner_text']).encode('ascii', 'ignore').replace('\r', '').expandtabs()])

        print table

        key = readchar.readchar().lower()

        while key != 'n' and key != 'q' and key != 'b':
            print 'b: switch to previous cluster'
            print 'n: switch to next cluster'
            print 'q: quit browser'
            key = readchar.readchar().lower()

        if key == 'n':
            i = i + 1
        elif key == 'b':
            i = 0 if i == 0 else (i - 1)
        else:
            break
