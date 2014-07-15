import os
import datetime
import glob
import distutils.dir_util
import shutil
import sys

import shellqueue

if len(sys.argv) != 3:
    print "make_task.py source target_environment"

source_directory = sys.argv[1]
target_base_directory = sys.argv[2]
project_name = os.path.basename(source_directory)

target_directory = os.path.join(target_base_directory, 'planning', project_name)
if os.path.exists(target_directory):
    n = 0
    while True:
        if len(project_name.split('-')) > 1 and project_name.split('-')[-1].isdigit():
            project_name = '-'.join(project_name.split('-')[:-1])
        target_directory = os.path.join(target_base_directory, "planning", "%s-%d" % (project_name, n))
        if os.path.exists(target_directory):
            n += 1
        else:
            break

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
