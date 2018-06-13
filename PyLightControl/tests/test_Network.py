import pytest
from queue import Queue
from multiprocessing import Process
from typing import Tuple

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint,TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import time

from PyLightControl import NetworkClient
from PyLightCommon.Globals import *

killFlag = False

class Server(Protocol):
    def __init__(self,factory):
        self.factory = factory

    def dataReceived(self,data):
        print(data)
        for process in self.interestedProcesses:
            process.put_message(data)

    def sendData(self,data: str):
        self.transport.write(data.encode())

    def addInterestedParties(self,process):
        try:
            self.interestedProcesses.append(process)
        except AttributeError:
            self.interestedProcesses = [process]

class ServerFactory(Factory):
    def buildProtocol(self,addr):
        self.localServer = Server(self)
        for process in self.interestedProcesses:
            self.localServer.addInterestedParties(process)
        return self.localServer

    def sendData(self,data):
        try:
            self.localServer.sendData(data)
        except Exception as e:
            print("NO SERVER")
            raise e

    def addInterestedParties(self,process):
        try:
            self.localServer.addInterestedParties(process)
        except AttributeError:
            try:
                self.interestedProcesses.append(process)
            except AttributeError:
                self.interestedProcesses = [process]

class DummyControl:
    def __init__(self):
        self.p = Process(target=self.startFactory, name='twisted')
        self.queue = Queue()
        self.killFlag = False
        self.p.start()

    def startFactory(self):
        endpoint = TCP4ServerEndpoint(reactor,port)

        self.factory = ServerFactory()
        self.factory.addInterestedParties(self)

        endpoint.listen(self.factory)
        reactor.run()

    def put_message(self,msg):
        self.queue.put(msg)

    def stop(self):
        reactor.callFromThread(reactor.stop)
        self.p.terminate()
        self.p.join()


@pytest.fixture(scope='module')
def functionSetup(request):
    control = DummyControl()
    def cleanup():
        control.stop()
    request.addfinalizer(cleanup)
    return NetworkClient(port,interface='lo'),control


def testAddressLookup(functionSetup : Tuple[NetworkClient,DummyControl]):
    nwClient,control = functionSetup
    assert nwClient.server_addres == '127.0.0.1'

def testCheckServer(functionSetup: Tuple[NetworkClient,DummyControl]):
    nwClient, control = functionSetup
    assert nwClient.checkServer('1','127.0.0.{0}') == '127.0.0.1'

def testCheckFindIP(functionSetup: Tuple[NetworkClient,DummyControl]):
    nwClient, control = functionSetup
    assert nwClient.get_ip_address('lo') == '127.0.0.1'

def testCheckIPParts(functionSetup: Tuple[NetworkClient,DummyControl]):
    nwClient, control = functionSetup
    assert nwClient.getIPParts('127.0.0.1') == (range(0,256),'127.0.0.{0}',['127','0','0','1'])