import argparse
import sys
import os.path
import pandas as pd
from beautifultable import BeautifulTable, ALIGN_LEFT
import unicodedata
import readchar

high_priority_file = 'high-priority.txt'
low_priority_file = 'low-priority.txt'

def clear_screen():
    print '\033c'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Command line viewer for clusters.')
    parser.add_argument('clusters_pickle', type=str, help='Cluster pickle file')
    parser.add_argument('cluster_id_column', type=str, help='Name of cluster ID column in the pickle file')
    parser.add_argument('-s', '--start', type=int, default=0, help='Optional index of cluster to start with (from 0)')
    parser.add_argument('-H', '--high-priority', action='store_true', default=False, help='Optionally read from the high priority list rather than sequentially through clusters')
    parser.add_argument('-L', '--low-priority', action='store_true', default=False, help='Optionally read from the low priority list rather than sequentially through clusters')
    args = parser.parse_args()

    reload(sys)
    sys.setdefaultencoding('utf-8')

    headers = None
    if not os.path.isfile(args.clusters_pickle):
        print 'Error: Cluster pickle file not found.'
        sys.exit(1)
    else:
        clusters_dataframe = pd.read_pickle(args.clusters_pickle)
        headers = ['index', 'hostname', 'inner_text', 'site_url']

    if args.high_priority or args.low_priority:
        priority_clusters = set()
        file = high_priority_file if args.high_priority else low_priority_file
        with open(file, 'r') as f:
            for line in f:
                priority_clusters.add(int(line))
        to_complete_clusters = clusters_dataframe[clusters_dataframe[args.cluster_id_column].isin(priority_clusters)]
    else:
        to_complete_clusters = clusters_dataframe
    to_complete_clusters_list = list(set(to_complete_clusters[args.cluster_id_column].tolist()))
    total_clusters = len(to_complete_clusters_list)
    to_complete_clusters_ids = to_complete_clusters_list[args.start:]
    to_complete_clusters_ids.sort(reverse = True )
    del to_complete_clusters_list

    count = len(to_complete_clusters_ids)
    i = 0

    high_priority_clusters = set()
    low_priority_clusters = set()

    if count == 0:
        print 'No clusters to browse'
        sys.exit(1)

    while i < count:
        clear_screen()
        current_id = to_complete_clusters_ids[args.start + i]
        current_cluster = clusters_dataframe[clusters_dataframe[args.cluster_id_column] == current_id]

        if (current_cluster.shape[0] > 5000):
            i = i + 1
            continue

        table = BeautifulTable(max_width=160, default_alignment=ALIGN_LEFT)
        table.column_headers = headers

        j = 1
        for index, row in current_cluster.iterrows():
            table.append_row([j, row['hostname'], unicodedata.normalize('NFKD', row['inner_text']).encode('ascii','ignore').replace('\r', '').expandtabs(), row['site_url']])
            j += 1

        print table
        print 'Cluster %d/%d (ID %d, %d segments)' % (args.start + i, total_clusters-1, current_id, current_cluster.shape[0])
        print

        key = ''
        valid_keys = ['b', 'n', 'h', 'l', 'q']
        while key not in valid_keys:
            print 'Enter a command:'
            print 'b: switch to previous cluster'
            print 'n: switch to next cluster'
            print 'h: mark high priority'
            print 'l: mark low priority'
            print 'q: save marked clusters and quit browser'
            sys.stdout.write('> ')
            sys.stdout.flush()
            key = readchar.readchar().lower()
            print key + '\n'
        if key == 'n':
            i = i + 1
        elif key == 'b':
            i = 0 if i == 0 else (i - 1)
        elif key == 'h':
            if current_id in low_priority_clusters:
                low_priority_clusters.remove(current_id)
            high_priority_clusters.add(current_id)
            i = i + 1
        elif key == 'l':
            if current_id in high_priority_clusters:
                high_priority_clusters.remove(current_id)
            low_priority_clusters.add(current_id)
            i = i + 1
        else:
            break

    with open(high_priority_file, 'a') as f:
        for s in high_priority_clusters:
            f.write(str(s) + '\n')
    with open(low_priority_file, 'a') as f:
        for s in low_priority_clusters:
            f.write(str(s) + '\n')

    print 'Ended at cluster %d/%d (ID %d)' % (args.start + i, total_clusters-1, current_id)
