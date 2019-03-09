import sys
import os.path
import pandas as pd
from beautifultable import BeautifulTable, ALIGN_LEFT
import unicodedata
import readchar

usage = 'Usage: python %s [cluster_file_pickle] [cluster_id_column] [start_index]' % __file__

RECORD_FILE = 'saved.txt'

def clear_screen():
    print '\033c'

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print usage
        sys.exit(1)

    clusters_pickle = sys.argv[1]
    cluster_id_col = sys.argv[2]
    start_index = int(sys.argv[3])

    reload(sys)
    sys.setdefaultencoding('utf-8')

    headers = None
    if not os.path.isfile(clusters_pickle):
        print 'Error: Cluster pickle file not found.'
        sys.exit(1)
    else:
        clusters_dataframe = pd.read_pickle(clusters_pickle)
        headers = ['hostname', 'inner_text', 'site_url']

    clusters = list(set(clusters_dataframe[cluster_id_col].tolist()))
    nclusters = len(clusters)
    to_complete_clusters_ids = clusters[start_index:]
    to_complete_clusters_ids.sort(reverse = True )
    del clusters

    count = len(to_complete_clusters_ids)
    i = 0

    saved_set = set()

    while i < count:
        clear_screen()
        current_id = to_complete_clusters_ids[start_index + i]
        current_cluster = clusters_dataframe[clusters_dataframe[cluster_id_col] == current_id]

        if (current_cluster.shape[0] > 5000):
            i = i + 1
            continue

        table = BeautifulTable(max_width=160, default_alignment=ALIGN_LEFT)
        table.column_headers = headers

        for index, row in current_cluster.iterrows():
            table.append_row([row['hostname'], unicodedata.normalize('NFKD', row['inner_text']).encode('ascii','ignore').replace('\r', '').expandtabs(), row['site_url']])

        print table
        print 'Cluster %d/%d (ID %d)' % (start_index + i, nclusters-1, current_id)
        print

        key = ''
        while key != 'n' and key != 's' and key != 'q' and key != 'b':
            print 'Enter a command:'
            print 'b: switch to previous cluster'
            print 'n: switch to next cluster'
            print 's: save current cluster'
            print 'q: write to file and quit browser'
            sys.stdout.write('> ')
            sys.stdout.flush()
            key = readchar.readchar().lower()
            print key + '\n'
        if key == 'n':
            i = i + 1
        elif key == 'b':
            i = 0 if i == 0 else (i - 1)
        elif key == 's':
            saved_set.add(current_id)
            i = i + 1
        else:
            break

    record_cluster_file = open(RECORD_FILE, 'a')

    for s in saved_set:
        record_cluster_file.write(str(s) + '\n')

    record_cluster_file.close()

    print 'Ended at cluster %d/%d (ID %d)' % (start_index + i, nclusters-1, current_id)
