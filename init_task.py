import os
import datetime
import glob
import distutils.dir_util
import shutil
import sys

import shellqueue

if len(sys.argv) != 3:
    print "make_task.py source target_environment"
    sys.exit()

source_directory = sys.argv[1]
target_base_directory = sys.argv[2]
project_name = os.path.basename(source_directory)

def project_exists(name):
    for tf in ['planning', 'scheduled', 'completed', 'processing']:
        target_directory = os.path.join(target_base_directory, tf, project_name)
        if os.path.exists(target_directory):
            return True
    else:
        return False

def make_next_name(project_name):
    if len(project_name.split('-')) > 1 and project_name.split('-')[-1].isdigit():
        num = int(project_name.split('-')[-1]) + 1
        project_name = '-'.join(project_name.split('-')[:-1] + [str(num),])
    else:
        project_name = project_name + '-0'
    return project_name

if project_exists(project_name):
    while True:
        project_name = make_next_name(project_name)
        if project_exists(project_name):
            pass
        else:
            break

target_directory = os.path.join(target_base_directory, 'planning', project_name)
os.makedirs(target_directory)

manifest_s_filename = os.path.join(source_directory, 'shellqueue.manifest')
if not os.path.exists(manifest_s_filename):
    with open(manifest_s_filename, 'w') as fh:
        fh.write("""%s

# Created on %s""" % (shellqueue.DEFAULT_MANIFEST_STR, datetime.datetime.now())
)
else:
    shutil.copy(manifest_s_filename, os.path.join(target_directory, 'shellqueue.manifest'))

print target_directory
