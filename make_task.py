import os
import datetime
import glob
import distutils.dir_util
import shutil
import sys

import shellqueue

if len(sys.argv) != 3:
    print "make_task.py source target"

source_directory = sys.argv[1]
target_directory = sys.argv[2]
project_name = os.path.basename(source_directory)

project_content = glob.glob(os.path.join(source_directory, '*'))
project_content = [pc.replace(source_directory + '/', '') for pc in project_content]

manifest_filename = os.path.join(target_directory, 'shellqueue.manifest')
manifest = shellqueue.parse_manifest(manifest_filename)

if manifest == shellqueue.DEFAULT_MANIFEST:
    # user hasn't changed anything from the default, abort
    print "Unchanged from default manifest, deleting new project"
    shutil.rmtree(target_directory)
else:
    print "Copying project data..."
    if 'output' in manifest:
        manifest_output_dir = manifest['output']

    try:
        project_content.remove('shellqueue.manifest')
    except:
        pass

    if manifest_output_dir is not None:
        try:
            project_content.remove(manifest_output_dir)
        except:
            pass
        try:
            project_content.remove(manifest_output_dir.strip('/'))
        except:
            pass

    for fe in project_content:
        source = os.path.join(source_directory, fe)
        target = os.path.join(target_directory, fe)
        print "%s -> %s" % (source, target)
        if os.path.isdir(source):
            distutils.dir_util.copy_tree(source, target)
        else:
            shutil.copyfile(source, target)
