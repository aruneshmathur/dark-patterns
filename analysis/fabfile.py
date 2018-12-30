from fabric.api import run, env, cd, prefix, put
import random
import string
import os

env.user='amathur'
env.hosts='portal.cs.princeton.edu'

def runbg(cmd, sockname='dtach'):
    return run('dtach -n `mktemp -u %s.XXXX` %s' % (sockname, cmd))

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
    put('script.sh', remote_dest)

    with cd(remote_dest):
        runbg('bash script.sh %s' % remote_db)
        #run('python feature_transformation.py')
        #run('python clustering')
