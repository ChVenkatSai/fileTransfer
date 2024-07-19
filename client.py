import os
import socket
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from hashlib import md5

class handler(FileSystemEventHandler):
    def __init__(self,host,port,filepath) -> None:
        self.host = host
        self.port = port
        self.filepath = filepath
        self.last_time = 0
    
    def send_update(self,event):
        now = time.time()
        if now-self.last_time<1:
            return
        self.last_time = now
        #print(now)
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.connect((self.host,self.port))

            filepath = self.filepath.ljust(1024,'\0').encode()
            s.sendall(filepath)

            file = self.filepath
            print(file)
            with open(file,'rb') as f:
                while chunk:=f.read(1024):
                    s.sendall(chunk)

    def on_created(self, event):
        return self.send_update(event)
    
    def on_modified(self, event):
        return self.send_update(event)

class Monitor:
    def __init__(self, filepath, chunksize) -> None:
        self.filepath = filepath
        self.checksum = []
        self.chunk = chunksize

    def computeChecksum(self, filepath):
        temp = []
        with open(filepath, 'rb') as f:
            while chunk:=f.read(self.chunk):
                temp.append(md5(chunk).hexdigest())
        return temp
    
    def compareChecksum(self):
        current = self.computeChecksum(self.filepath)
        comparision = []
        #print(len(self.checksum))
        for i, individualSum in enumerate(current):
            if i>len(self.checksum)-1 or current[i]!=self.checksum[i]:
                comparision.append((i, current[i]))

        self.checksum = current

        return comparision

class fileSend:
    def __init__(self,host,port,filepath,chunksize) -> None:
        self.host = host
        self.port = port
        self.filepath = filepath
        self.chunk = chunksize

    def send(self):
        #print(os.path.exists(self.filepath))
        monitor = Monitor(self.filepath, self.chunk)
        while True:
            time.sleep(1)
            changes = monitor.compareChecksum()
            print(f'length of changes {len(changes)}')
            if len(changes) == 0:
                continue
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                s.connect((self.host,self.port))
                filepath = self.filepath.ljust(self.chunk,'\0').encode()
                s.sendall(filepath)
                with open(self.filepath,'rb') as f:
                    for i, checksum in changes:
                        f.seek(i*self.chunk)
                        data = f.read(self.chunk)
                        #print(i)
                        index = str(i)
                        index = index.ljust(self.chunk,'\0')
                        #print(index)
                        s.sendall(index.encode())
                        s.sendall(data)
            

        directory_to_watch = os.path.dirname(self.filepath)
        event_handler = handler(self.host,self.port,self.filepath)
        observer = Observer()
        #print(self.filepath)
        observer.schedule(event_handler, path=directory_to_watch,recursive=False)

        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

if __name__ == '__main__':
    
    client = fileSend('127.0.0.1',5000,'./source/garbage.txt', 32)
    client.send()