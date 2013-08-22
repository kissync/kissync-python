import datetime
import os
import threading
import time

from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

import common
from definitions import LocalFile


class Watcher(threading.Thread):
    def __init__(self, parent, api, syncDir):
        threading.Thread.__init__(self)
        self.parent = parent
        self.api = api
        self.syncDir = syncDir

    def run(self):
        self.event_handler = EventHandler(self, self.parent, self.api)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.syncDir, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()


class EventHandler(FileSystemEventHandler):
    def __init__(self, parent, synchronizer, api):
        self.parent = parent
        self.synchronizer = synchronizer
        self.api = api
        self.syncDir = self.parent.syncDir
        self._timeoffset = common.calculate_time_offset()

    def on_moved(self, event):
        print "Item Moved:", event.src_path, event.dest_path
        serverPath = self.localToServerPath(event.src_path)
        serverPathNew = self.localToServerPath(event.dest_path)
        print "Server Path:", serverPath
        print "Server Path New:", serverPathNew
        try:
            print self.api.post('/path/oper/move/', src=serverPath, dst=serverPathNew)
        except:
            raise

    def on_created(self, event):
        print "Item Created:", event.src_path
        path = event.src_path
        serverPath = self.localToServerPath(path)
        #TODO: Test this on other platforms than Linux
        if not serverPath.startswith("/"):
            serverPath = os.path.join("/", serverPath)
        if not event.is_directory:
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
            checksum = common.getFileHash(path)
            size = int(os.path.getsize(path))
            isDir = os.path.isdir(path)
            localfile = LocalFile(serverPath, checksum, None, modified, size, isDir)

            #TODO: Something weird is happening here. When passing localfile
            #to the upload queue, SmartFile returns a 404 when seting the
            #attributes for the file
            #TODO: The error is caused when the file does not have a leading
            #forward slash
            print "Watcher file information"
            print localfile.path
            print localfile.checksum
            print localfile.modified_local
            self.synchronizer.uploadQueue.put(localfile)
        else:
            try:
                self.api.post('/path/oper/mkdir/', path=serverPath)
            except:
                raise

    def on_deleted(self, event):
        print "Item Deleted:", event.src_path
        try:
            self.api.post('/path/oper/remove', path=event.src_path)
        except:
            raise

    def on_modified(self, event):
        print "Item Modified:", event.src_path
        path = event.src_path
        serverPath = self.localToServerPath(path)
        if not event.is_directory:
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
            checksum = common.getFileHash(path)
            size = int(os.path.getsize(path))
            isDir = os.path.isdir(path)
            localfile = LocalFile(serverPath, checksum, None, modified, size, isDir)

            self.synchronizer.syncUpQueue.put(localfile)
        """
        else:
            try:
                self.parent.smartfile.post('/path/oper/mkdir/', path=serverPath)
            except:
                raise
        """

    def localToServerPath(self, path):
        pathOnServer = path.replace(self.syncDir, '')
        if pathOnServer.startswith("/"):
            pathOnServer = pathOnServer.strip("/")
        elif pathOnServer.startswith("\\"):
            pathOnServer = pathOnServer.strip("\\")
        return pathOnServer
