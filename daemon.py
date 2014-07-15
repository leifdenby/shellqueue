import os
import sys
import yaml
import time
import glob
import shutil
import subprocess
import threading

import shellqueue

if not len(sys.argv) == 2:
    print "First argument should be project folder"
else:
    project_folder = sys.argv[1]

def popenAndCall(onExit, popenArgs, cwd, log_filename):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that 
    would give to subprocess.Popen.
    """
    def runInThread(onExit, popenArgs, cwd, log_filename):
        with open(log_filename, 'w') as fh:
            proc = subprocess.Popen(popenArgs, cwd=cwd, stderr=fh, stdout=fh)
            proc.wait()
            onExit()
            return
    thread = threading.Thread(target=runInThread, args=(onExit, popenArgs, cwd, log_filename))
    thread.start()
    # returns immediately after the thread starts
    return thread

def run_task(project_folder):
    manifest_filename = os.path.join(project_folder, 'shellqueue.manifest')
    manifest = shellqueue.parse_manifest(manifest_filename)
    cmd_args = [manifest['exec'],]

    src = project_folder
    dst = project_folder.replace('/scheduled/', '/processing/')

    shutil.move(src, dst)

    output_folder = os.path.join(dst, manifest['output'])
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    def start():

        print "Starting project in %s" % project_folder

        num_repeats = 0
        def cleanup_f():
            if 'repeats' in manifest and num_repeats < int(manifest['repeats']):
                num_repeats += 1
                start()
            else:
                src = project_folder.replace('/scheduled/', '/processing/')
                dst = project_folder.replace('/scheduled/', '/completed/')

                shutil.move(src, dst)

        popenAndCall(onExit=cleanup_f, popenArgs=manifest['exec'], cwd=dst, log_filename=os.path.join(dst, 'run.log'))

    start()

print "Ready..."

running_tasks = 0
while True:
    scheduled_projects_path = os.path.join(project_folder, 'scheduled', '*')
    scheduled_tasks = glob.glob(scheduled_projects_path)

    if len(scheduled_tasks) > 0:
        scheduled_tasks.sort(key=lambda x: os.stat(x).st_mtime)
        t = scheduled_tasks[0]
        run_task(t)
        scheduled_tasks.remove(t)

    processing_projects_path = os.path.join(project_folder, 'processing', '*')
    processing_tasks = glob.glob(processing_projects_path)

    print "%s: %d scheduled, %d processing" % (time.strftime('%X %x %Z'), len(scheduled_tasks), len(processing_tasks))

    time.sleep(1)