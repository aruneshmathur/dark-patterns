from fabric.api import run, env, cd, prefix, put
import random
import string
import os

env.hosts=['cycles.cs.princeton.edu']
env.user='mjf4'
remote_root = '/u/%s' % env.user

def runbg(cmd, sockname='dtach'):
    return run('dtach -n `mktemp -u %s.XXXX` %s' % (sockname, cmd))

def deploy():
    remote_dir = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    remote_dest = os.path.join(remote_root, remote_dir)

    remote_db = '/n/fs/darkpatterns/crawl/2018-12-08_segmentation_pilot2/2018-12-08_segmentation_pilot2.sqlite'

    with cd(remote_root):
        run('mkdir ' + remote_dir)

    put('preprocessing.py', remote_dest)
    put('feature_transformation.py', remote_dest)
    put('clustering.py', remote_dest)
    put('clustering.sh', remote_dest)

    with cd(remote_dest):
        runbg('bash clustering.sh %s' % remote_db)

    print 'Running clustering in bg in remote directory %s' % remote_dest
