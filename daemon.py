import os
import sys
import yaml
import time
import datetime
import glob
import shutil
import subprocess
import threading
import multiprocessing
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import dateutil.parser

import shellqueue

DATETIME_FORMAT = "%X %x %Z"

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
        with open(log_filename, 'a') as fh:
            fh.write("# Log opened at %s" % time.strftime(DATETIME_FORMAT))
            fh.flush()
            proc = subprocess.Popen(popenArgs, cwd=cwd, stderr=fh, stdout=fh)
            proc.wait()
            onExit()
            return
    thread = threading.Thread(target=runInThread, args=(onExit, popenArgs, cwd, log_filename))
    thread.start()
    # returns immediately after the thread starts
    return thread

def run_task(project_folder, task_complete_callback):
    manifest_filename = os.path.join(project_folder, 'shellqueue.manifest')
    manifest = shellqueue.parse_manifest(manifest_filename)
    cmd_args = [manifest['exec'],]

    src = project_folder
    dst = project_folder.replace('/scheduled/', '/processing/')

    shutil.move(src, dst)

    output_folder = os.path.join(dst, manifest['output'])
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    def start(run_num):

        print "Starting project in %s" % project_folder

        def cleanup_f():
            if 'repeats' in manifest and run_num < int(manifest['repeats']):
                start(run_num+1)
            else:
                src = project_folder.replace('/scheduled/', '/processing/')
                dst = project_folder.replace('/scheduled/', '/completed/')

                shutil.move(src, dst)
                task_complete_callback()

        popenAndCall(onExit=cleanup_f, popenArgs=manifest['exec'], cwd=dst, log_filename=os.path.join(dst, 'run.log'))

    start(0)


running_tasks = []
max_tasks = multiprocessing.cpu_count()



def td_format(td_object):
    # http://stackoverflow.com/questions/538666/python-format-timedelta-to-string
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings=[]
    for period_name,period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds,period_seconds)
            if period_value == 1:
                strings.append("%s %s" % (period_value, period_name))
            else:
                strings.append("%s %ss" % (period_value, period_name))

    return ", ".join(strings)



def get_scheduled_tasks():
    scheduled_projects_path = os.path.join(project_folder, 'scheduled', '*')
    return glob.glob(scheduled_projects_path)

def get_processing_tasks():
    processing_projects_path = os.path.join(project_folder, 'processing', '*')
    return glob.glob(processing_projects_path)

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()

        scheduled_tasks = get_scheduled_tasks()
        processing_tasks = get_processing_tasks()
        lines = [
            "shellqueue",
            "==========",
            "",
            "%s: %d scheduled, %d processing" % (time.strftime('%X %x %Z'), len(scheduled_tasks), len(processing_tasks)),
            "",
            "",
        ]

        for task_path in processing_tasks:
            t = ShellQueueTask(task_path)
            log, last_modified, first_entry_at, _ = t.get_log()

            running_for = last_modified - first_entry_at

            title = '%s (%s), running %s' % (task_path, last_modified.strftime(DATETIME_FORMAT).strip(), td_format(running_for))

            repeat_count = t.get_repeat_count()
            if repeat_count is not None:
                title += ' ' + repeat_count

            lines += [title, '-' * len(title), "", ]

            lines += log[-10:]

        message = "\n".join(lines)


        self.wfile.write(message)
        return

class ShellQueueTask():
    def __init__(self, path):
        self.path = path

    def get_log(self):
        filename = os.path.join(self.path, 'run.log')
        last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(filename))

        log_lines = open(filename).read().splitlines()

        log_opened_at_str = None
        n_repeats = 0
        for l in log_lines:
            if l.startswith('# Log opened at'):
                if log_opened_at_str is None:
                    log_opened_at_str = l.replace('# Log opened at ','')
                n_repeats += 1

        first_modified = datetime.datetime.strptime(log_opened_at_str, DATETIME_FORMAT)

        return log_lines, last_modified, first_modified, n_repeats

    @property
    def manifest(self):
        manifest_filename = os.path.join(self.path, 'shellqueue.manifest')
        return shellqueue.parse_manifest(manifest_filename)

    def get_repeat_count(self):
        manifest = self.manifest

        if 'repeats' in manifest:
            _, _, _, repeat_num = self.get_log()

            return '@%s/%s' % (repeat_num, manifest['repeats'])
        else:
            return None

def check_for_tasks():
    while True:
        scheduled_tasks = get_scheduled_tasks()
        processing_tasks = get_processing_tasks()

        if len(scheduled_tasks) > 0 and len(running_tasks) < max_tasks:
            scheduled_tasks.sort(key=lambda x: os.stat(x).st_mtime)
            t = scheduled_tasks[0]
            run_task(t, lambda: running_tasks.remove(t))
            running_tasks.append(t)
            scheduled_tasks.remove(t)

        print "%s: %d scheduled, %d processing" % (time.strftime(DATETIME_FORMAT), len(scheduled_tasks), len(processing_tasks))

        time.sleep(1)

if __name__ == "__main__":
    t = threading.Thread(target=check_for_tasks)
    t.daemon = True
    t.start()

    print "Ready..."

    server = HTTPServer(('0.0.0.0', 8080), GetHandler)
    server.serve_forever()
