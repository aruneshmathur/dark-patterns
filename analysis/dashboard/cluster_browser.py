import sys
import os.path
import pandas as pd
from beautifultable import BeautifulTable, ALIGN_LEFT
import unicodedata
import readchar

COMPLETED_FILE = 'completed.txt'
RECORD_FILE = 'saved.txt'

def clear_screen():
    print '\033c'

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print 'Usage: python cluster_browser.py [cluster_file_pickle] [cluster_id_column]'
        sys.exit(1)

    reload(sys)
    sys.setdefaultencoding('utf-8')

    headers = None
    if not os.path.isfile(sys.argv[1]):
        print 'Error: Cluster pickle file not found.'
        sys.exit(1)
    else:
        cluster_dataframe = pd.read_pickle(sys.argv[1])
        headers = [sys.argv[2], 'hostname', 'inner_text']

    completed_clusters = []
    if os.path.isfile(COMPLETED_FILE):
        with open(COMPLETED_FILE, 'r') as f:
            # Read all the clusters completed so far
            for l in f.readlines():
                completed_clusters.append(l.strip())

    to_complete_clusters = cluster_dataframe[~cluster_dataframe[sys.argv[2]].isin(completed_clusters)]
    to_complete_clusters_ids = list(set(to_complete_clusters[sys.argv[2]].tolist()))
    to_complete_clusters_ids.sort(reverse = True )

    count = len(to_complete_clusters_ids)
    i = 0

    viewed_set = set()
    saved_set = set()

    while i < count:
        clear_screen()
        current_id = to_complete_clusters_ids[i]
        current_cluster = to_complete_clusters[to_complete_clusters[sys.argv[2]] == current_id]

        if (current_cluster.shape[0] > 5000):
            i = i + 1
            continue

        table = BeautifulTable(max_width=160, default_alignment=ALIGN_LEFT)
        table.column_headers = headers

        for index, row in current_cluster.iterrows():
            table.append_row([row[sys.argv[2]], row['hostname'], unicodedata.normalize('NFKD', row['inner_text']).encode('ascii','ignore').expandtabs()])

        print table

        key = readchar.readchar().lower()

        while key != 'n' and key != 's' and key != 'q' and key != 'b':
            print 'b: switch to previous cluster'
            print 'n: switch to next cluster'
            print 's: save current cluster'
            print 'q: write to file and quit browser'
            key = readchar.readchar().lower()

        if key == 'n':
            viewed_set.add(current_id)
            i = i + 1
        elif key == 'b':
            i = 0 if i == 0 else (i - 1)
        elif key == 's':
            saved_set.add(current_id)
            viewed_set.add(current_id)
            i = i + 1
        else:
            break

    completed_cluster_file = open(COMPLETED_FILE, 'a')
    record_cluster_file = open(RECORD_FILE, 'a')

    for v in viewed_set:
        completed_cluster_file.write(str(v) + '\n')

    for s in saved_set:
        record_cluster_file.write(str(s) + '\n')

    record_cluster_file.close()
    completed_cluster_file.close()
