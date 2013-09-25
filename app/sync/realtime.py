import hashlib
import os
import thread
import threading
import time
import uuid
import websocket
try:
    import simplejson as json
except ImportError:
    import json

import common
from definitions import RemoteFile


class RealtimeSync(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.websocket_address = "ws://198.58.119.99:8888/sync"

        # Generate a UUID for this client
        self.auth_uuid = str(uuid.uuid1())

        self.connected = False
        self.authenticated = False

    def run(self):
        while True:
            self.create_connection()
            self.ws.run_forever()
            # if the client disconnects, delay, then reconnect
            time.sleep(10)

    def create_connection(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.websocket_address,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close)
        self.ws.on_open = self.on_open

    def processSendQueue(self, *args):
        """
        Send changes that occured when the client was offline
        to the realtime sync server
        """
        taskInQueue = False
        while True:
            while self.connected and self.authenticated:
                # Check if a task is already loaded
                if taskInQueue is False:
                    # This blocks until it gets a task
                    object = self.parent.changesQueue.get()
                taskInQueue = True
                if self.connected is False or self.authenticated is False:
                    break
                self.ws.send(object)
                self.parent.changesQueue.task_done()
                taskInQueue = False
            time.sleep(1)

    def _sendChanges(self, changes):
        # Prepare the dictionary to send
        send_data = {'uuid': self.auth_uuid}
        send_data.update(changes)
        data = json.dumps(send_data)

        if self.connected and self.authenticated:
            # send the json encoded message
            self.ws.send(data)
        else:
            self.parent.changesQueue.put(data)

    def update(self, path, change_type, size, isDir, destination):
        """
        use this method to send updates to the server
        use the following for change_type:
            created_file, created_dir, modified, deleted, moved
        """
        send_data = {'path': path, 'type': change_type, 'size': size, 'isDir':
                isDir, 'dest': destination}
        self._sendChanges(send_data)

    def on_message(self, ws, message):
        json_data = json.loads(message)

        if 'created_file' in json_data:
            path = json_data['path']
            checksum = "123"  # Provide something not None
            modified = None
            size = json_data['size']
            isDir = False
            remotefile = RemoteFile(path, checksum, modified, size, isDir)
            self.parent.downloadQueue.put(remotefile)
        elif 'created_dir' in json_data:
            path = json_data['path']
            checksum = "123"
            modified = None
            size = 0
            isDir = True
            remotefile = RemoteFile(path, checksum, modified, size, isDir)
            self.parent.downloadQueue.put(remotefile)
        elif 'modified' in json_data:
            path = json_data['path']
            checksum = "123"
            modified = None
            size = json_data['size']
            isDir = False
            remotefile = RemoteFile(path, checksum, modified, size, isDir)
            if self.parent.syncLoaded:
                self.parent.syncDownQueue.put(remotefile)
            else:
                self.parent.downloadQueue.put(remotefile)
        elif 'deleted' in json_data:
            serverPath = json_data['path']
            path = common.basePath(serverPath)
            absolutePath = os.path.join(self.parent._syncDir, path)
            if json_data['isDir']:
                os.rmdir(absolutePath)
            else:
                os.remove(absolutePath)
        elif 'moved' in json_data:
            serverPath = json_data['path']
            path = common.basePath(serverPath)
            absolutePath = os.path.join(self.parent._syncDir, path)
            common.createLocalDirs(os.path.dirname(os.path.realpath(absolutePath)))
            destination = json_data['dest']
            destPath = common.basePath(destination)
            absoluteDest = os.path.join(self.parent._syncDir, destPath)

            os.rename(absolutePath, absoluteDest)

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        self.connected = False
        self.authenticated = False
        print("Disconnected from the realtime sync server")

    def on_open(self, ws):
        self.connected = True

        # authenticate the client
        token = self.config.get("Login", "token")
        verifier = self.config.get("Login", "verifier")

        auth_hash = hashlib.md5()
        auth_hash.update("%s%s" % (token, verifier))
        auth_string = auth_hash.hexdigest()

        auth_data = {'authentication': auth_string, 'uuid': self.auth_uuid}
        json_data = json.dumps(auth_data)

        # send the auth data to the server
        self.ws.send(json_data)

        self.authenticated = True

        # start the thread to process the queue of changes
        thread.start_new_thread(self.processSendQueue, ())
