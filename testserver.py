from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from PyLightTestServer import ServerFactory
from Support.Globals import *

def commander(factory: ServerFactory):
    print("-----------------------------------------------------------")
    print("Welcome to Commander, your personal assistant to controlling your home automation system")
    print("-----------------------------------------------------------")
    print("Please input your commands")
    while True:
        cmd = input()
        reactor.callFromThread(factory.sendData,str.encode(cmd))

def startThreads():
    endpoint = TCP4ServerEndpoint(reactor,port)
    factory = ServerFactory()
    endpoint.listen(factory)
    reactor.callInThread(commander,factory)
    reactor.run()

startThreads()