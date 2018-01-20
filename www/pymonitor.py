# -*- coding: utf-8 -*-
'Auto Restart process when source code changed'
__autor__ = 'ZAM';

from watchdog.events import FileSystemEventHandler;
from watchdog.observers import Observer;
import subprocess;
import sys;
import os;
import time;

command = ['python', 'you-script.py'];
process = None;

def log(s):
    print('[Monitor]%s'%s);

class MyFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, fn):
        super(MyFileSystemEventHandler, self).__init__();
        self.RestartFn = fn;
    
    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            log('Python Source File Changed: %s'%event.src_path);
            if callable(self.RestartFn):
                self.RestartFn();

def kill_process():
    global process;
    if process:
        log('kill process [%s]...'%(process.pid));
        process.kill();
        process.wait();
        log('process ended with returncode: %s'%(process.returncode));
        process = None;

def start_process():
    global process;
    log('start process [%s]...'%(' '.join(command)));
    if process:
        kill_process();
    process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr);

def restart_process():
    kill_process();
    start_process();

def start_watchdog(path, callback):
    observer = Observer();
    observer.schedule(MyFileSystemEventHandler(restart_process), path, recursive=True);
    observer.start();
    log('watching directory %s ...'%path);
    start_process();
    try:
        while True:
            time.sleep(0.5);
    except KeyboardInterrupt:
        observer.stop();
    observer.join();

if __name__ == '__main__':
    argv = sys.argv[1:];
    if not argv:
        print('Usage: ./pymonitir your-script.py');
        exit(0);
    if argv[0] != 'python':
        argv.insert(0, 'python');
    command = argv;
    path = os.path.abspath('.');
    start_watchdog(path, None);
