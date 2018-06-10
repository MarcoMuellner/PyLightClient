import socket
import fcntl
import struct
import binascii
from twisted.internet.protocol import Protocol

import time

from PyLightSupport.Commandos import *

class NetworkClient(Protocol):
    def __init__(self, port: int, addr: str = '',interface = 'wlan0'):
        self.killFlag = False
        self.runInitProces(port,addr,interface)

    def runInitProces(self,port,addr = "",interface = 'wlan0'):
        self.ip = self.get_ip_address(interface)
        self.macAddress = self.getHwAddr(interface)
        print(self.ip)
        self.port = port

        if addr is not '' and len(addr.split('.')) == 4:
            _, ipTemplate, ipParts = self.getIPParts(addr)
            ip = self.checkServer(ipParts[3], ipTemplate)
            if ip != '':
                print(f"Found server at {ip}")
                self.server_addres = addr
            else:
                self.server_addres = self.getServer()
        else:
            self.server_addres = self.getServer()

    def getServer(self) -> tuple:
        ipList,ipTemplate,_ = self.getIPParts(self.ip)

        while True:
            for i in ipList:
                if self.killFlag:
                    return
                ip = self.checkServer(i,ipTemplate)
                if ip != '':
                    print(f"Found server at {ip}")
                    return ip
            print("Cannot find a valid server!")
            time.sleep(10)

    def checkServer(self,i,ipTemplate):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, 0))
        print("Checking address {0}".format(ipTemplate.format(i)))
        socket.setdefaulttimeout(1)
        result = sock.connect_ex((ipTemplate.format(i), self.port))
        if result is 0:
            sock.close()
            return ipTemplate.format(i)
        sock.close()
        return ''

    def getIPParts(self,ip):
        ipList = range(0, 256)
        ipParts = ip.split(".")
        ipTemplate = ipParts[0] + '.' + ipParts[1] + '.' + ipParts[2] + '.{0}'

        return ipList,ipTemplate,ipParts

    def sendMessage(self,msg : str):
        self.transport.write(msg.encode())

    def dataReceived(self,data):
        print(f"Data received: {data}")
        self.notifyInterestedParties(data)

    def registerProces(self, process):
        try:
            self.registeredProcesses.append(process)
        except AttributeError:
            self.registeredProcesses = [process]

    def get_ip_address(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack(b'256s', str.encode(ifname[:15]))
        )[20:24])

    def getHwAddr(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(ifname[:15], 'utf-8')))
        return ''.join(l + ':' * (n % 2 == 1) for n, l in enumerate(binascii.hexlify(info[18:24]).decode('utf-8')))[:-1]

    def connectionMade(self):
        print("Client connected!")
        self.notifyInterestedParties(str.encode(cmd_client_connected[0]))

    def connectionLost(self,reason):
        print(f"Connection lost due to {reason}")
        self.notifyInterestedParties(str.encode(cmd_client_disconnected[0]))


    def notifyInterestedParties(self,data):
        for process in self.registeredProcesses:
            process.put_message(data)


