from fabric.api import run, env, cd, prefix, put
import random
import string
import os

env.user='amathur'
env.hosts='portal.cs.princeton.edu'

def deploy():
    remote_root = '/n/fs/darkpatterns/analysis'
    remote_dir = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    remote_dest = os.path.join(remote_root, remote_dir)

    remote_db = '/n/fs/darkpatterns/crawl/2018-12-08_segmentation_pilot2/2018-12-08_segmentation_pilot2.sqlite'

    with cd(remote_root):
        run('mkdir ' + remote_dir)


    put('clustering/clustering.py', remote_dest)
    put('clustering/feature_transformation.py', remote_dest)
    put('clustering/preprocessing.py', remote_dest)

    with cd(remote_dest):
        with prefix('source ' + os.path.join('/n/fs/darkpatterns/analysis', 'dp/bin/activate')):
            run('python preprocessing.py ' + remote_db)
            run('python feature_transformation.py')
            run('python clustering')
