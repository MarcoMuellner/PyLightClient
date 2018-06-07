from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

class Server(Protocol):
    def __init__(self,factory):
        self.factory = factory

    def connectionMade(self):
        print("Client connected!")

    def connectionLost(self,reason):
        print(f"Connection lost due to {reason}")

    def dataReceived(self,data):
        print(f"Data received: {data}")

    def sendData(self,data):
        self.transport.write(data)


class ServerFactory(Factory):
    def buildProtocol(self,addr):
        print("Building protocol ...")
        self.localServer = Server(self)
        return self.localServer

    def sendData(self,data):
        try:
            self.localServer.sendData(data)
        except:
            print("No local server available!")
