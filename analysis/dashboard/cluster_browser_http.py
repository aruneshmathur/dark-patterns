from flask import Flask
import argparse
import sys
import os.path
import pandas as pd
import unicodedata

app = Flask(__name__)

# Returns HTML for cluster id i
def generate_html(i, cluster_ids, clusters_dataframe, total_clusters, cluster_id_column):
    current_id = cluster_ids[i]
    current_cluster = clusters_dataframe[clusters_dataframe[cluster_id_column] == current_id]

    # Headers
    headers = ['index', 'hostname', 'inner_text', 'site_url']
    table = "<table border=1><tr>"
    for h in headers:
        table += "<th>%s</th>" % h
    table += "</tr>"

    # Values
    j = 1
    for index, row in current_cluster.iterrows():
        hostname = '<a href="%s">%s</a>' % (row['hostname'], row['hostname'])
        inner_text = unicodedata.normalize('NFKD', row['inner_text']).encode('ascii','ignore').replace('\r', '').expandtabs()
        site_url = '<a href="%s">%s</a>' % (row['site_url'], row['site_url'])
        values = [str(j), hostname, inner_text, site_url]
        table += "<tr>"
        for v in values:
            table += "<td>%s</td>" % v
        table += "</tr>"
        j += 1
    table += "</table>"
    message = 'Cluster %d/%d (ID %d, %d segments)' % (i, total_clusters-1, current_id, current_cluster.shape[0])

    # Next/back buttons
    back_button = '<a href="/%d" style="margin-right: 10px" class="button">Back</a>' % (i-1)
    next_button = '<a href="/%d" style="margin-right: 10px" class="button">Next</a>' % (i+1)

    html = back_button + next_button + '<br>' + message + '<br>' + table + '<br>' + message + '<br>' + back_button + next_button
    return html

@app.route('/')
def index():
    return generate_html(0, app.config['cluster_ids'], app.config['clusters_dataframe'], app.config['total_clusters'], app.config['cluster_id_column'])

@app.route('/<index>')
def get_cluster_index(index):
    index = int(index)
    message = ''
    if index >= len(app.config['cluster_ids']):
        message = '<b>There is no cluster index %d. Showing the last cluster instead (%d).</b><br>' % (index, len(app.config['cluster_ids']) - 1)
        index = len(app.config['cluster_ids']) - 1
    elif index < 0:
        message = '<b>There is no cluster index %d. Showing the first cluster instead (0).</b><br>' % index
        index = 0
    html = generate_html(index, app.config['cluster_ids'], app.config['clusters_dataframe'], app.config['total_clusters'], app.config['cluster_id_column'])
    return message + html

if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser(description='Web browser viewer for clusters. Go to the index page to begin viewing, or you can go to /<index> to view the cluster at a particular index (e.g. /10 to view cluster at index 10)')
    parser.add_argument('clusters_pickle', type=str, help='Cluster pickle file')
    parser.add_argument('cluster_id_column', type=str, help='Name of cluster ID column in the pickle file')
    args = parser.parse_args()

    # Load data
    reload(sys)
    sys.setdefaultencoding('utf-8')

    if not os.path.isfile(args.clusters_pickle):
        print 'Error: Cluster pickle file not found.'
        sys.exit(1)
    else:
        clusters_dataframe = pd.read_pickle(args.clusters_pickle)

    cluster_ids = list(set(clusters_dataframe[args.cluster_id_column].tolist()))
    total_clusters = len(cluster_ids)
    cluster_ids.sort(reverse=True)

    # Run server
    app.config['clusters_dataframe'] = clusters_dataframe
    app.config['cluster_ids'] = cluster_ids
    app.config['total_clusters'] = total_clusters
    app.config['cluster_id_column'] = args.cluster_id_column
    app.run()
