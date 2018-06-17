import logging
import socket
import fcntl
import struct
import binascii
import time
import requests
from requests.exceptions import ConnectTimeout,ConnectionError

from PyLightCommon.Commandos import *

logger = logging.getLogger(__name__)

def getServer(hostIP) -> tuple:
    ipList,ipTemplate,_ = getIPParts(hostIP)

    while True:
        for i in ipList:
            logger.debug(f"Checking server at {ipTemplate.format(i)}")
            ip = checkServer(ipTemplate.format(i))
            if ip != '':
                print(f"Found server at {ip}")
                return ip
        print("Cannot find a valid server!")
        time.sleep(10)

def checkServer(ip):

    response = requests.get(f"http://{ip}:8000/hardwareRequest",params={"cmd":cmd_alive[0]},timeout=1)
    logger.info(f"Got response with status code {response.status_code} and text {response.text}")
    if response.status_code == 200 and response.text == cmd_ok[0]:
        return ip

def getIPParts(ip):
    ipList = range(1, 256)
    ipParts = ip.split(".")
    ipTemplate = ipParts[0] + '.' + ipParts[1] + '.' + ipParts[2] + '.{0}'

    return ipList,ipTemplate,ipParts

def getIPAddress(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack(b'256s', str.encode(ifname[:15]))
    )[20:24])

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(ifname[:15], 'utf-8')))
    return ''.join(l + ':' * (n % 2 == 1) for n, l in enumerate(binascii.hexlify(info[18:24]).decode('utf-8')))[:-1]
