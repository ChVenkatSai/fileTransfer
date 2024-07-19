import os
import time
import socket

class FileRec:
    def __init__(self, port, host, target_dir, chunksize) -> None:
        self.port = port
        self.host = host
        self.target_dir = target_dir
        self.chunk = chunksize

    def serve(self):
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.bind((self.host,self.port))
            s.listen()

            while True:
                con, address = s.accept()
                with con:
                    print(f"Address is {address}")
                    filepath = con.recv(self.chunk).decode().strip('\0')

                    target = os.path.join(self.target_dir, os.path.basename(filepath))
                    print(target)
                    with open(target, "r+b") as f:
                        while True:
                            index =  (con.recv(self.chunk).decode().strip('\0'))
                            if index == '':
                                break
                            index = int(index)
                            print(index)
                            f.seek(index*self.chunk)
                            data = con.recv(self.chunk)
                            if data==b'':
                                break
                            print(data)
                            f.write(data)

if __name__ == '__main__':
    server = FileRec(5000,'127.0.0.1','destination', 32)
    server.serve()