import socket
from twisted.internet.protocol import Protocol

import time

from PyLightControl import Control


class NetworkClient(Protocol):
    def __init__(self, port: int, addr: str = ''):
        self.ip = socket.gethostbyname(socket.gethostname())
        print(self.ip)
        self.port = port

        if addr is not '' and len(addr.split('.')) == 4:
            self.server_addres = addr
        else:
            self.server_addres= self.getServer()

    def getServer(self) -> tuple:
        ipList = range(0,256)
        ipParts = self.ip.split(".")
        ipTemplate = ipParts[0]+'.'+ipParts[1]+'.'+ipParts[2]+'.{0}'

        while True:
            for i in ipList:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("Checking address {0}".format(ipTemplate.format(i)))
                socket.setdefaulttimeout(1)
                result = sock.connect_ex((ipTemplate.format(i),self.port))
                if result is 0:
                    print(f"Found server at {ipTemplate.format(i)}")
                    return ipTemplate.format(i)
                sock.close()
            print("Cannot find a valid server!")
            time.sleep(10)

    def sendMessage(self,msg : str):
        self.transport.write(msg.encode())

    def dataReceived(self,data):
        print(data)
        for process in self.registeredProcesses:
            process.put_message(data)

    def registerProces(self,process : Control):
        try:
            self.registeredProcesses.append(process)
        except AttributeError:
            self.registeredProcesses = [process]


