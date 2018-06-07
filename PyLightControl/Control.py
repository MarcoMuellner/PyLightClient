from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
from queue import Queue

from PyLightHardware import GPIOControl
from PyLightControl.Network import NetworkClient
from Support.Globals import *
from Support.Commandos import *

import time



class Controller:
    def __init__(self):
        self.hwControl = GPIOControl()
        #TODO previously read from db if we already have an old connection
        self.nwClient = NetworkClient(port)
        self.queue = Queue()

        self.startProcesses()

    def startProcesses(self):
        self.nwClient.registerProces(self)
        point = TCP4ClientEndpoint(reactor,self.nwClient.server_addres,port)
        connectProtocol(point,self.nwClient)
        reactor.callInThread(self.worker)
        reactor.run()

    def worker(self):
        self.sendNetworkMessage(cmd_signup[0])
        print("STARTING COMMAND LOOP!")
        while True:
            message = self.queue.get()
            self.parse_message(message)


    def setupHardware(self):
        #TODO read all old states from database, and set them accordingly
        pass

    def put_message(self,msg):
        self.queue.put(msg)

    def parse_message(self,msg:bytes):
        msgParts = msg.decode().split(":")

        if str(msgParts[0]) == cmd_welcome[0]:
            self.checkMessage(msgParts,cmd_welcome)
            self.name = msgParts[1]
            allIOS = self.hwControl.allIOs
            self.sendNetworkMessage(cmd_all_io_list[0]+f":{self.name}:{allIOS}")
            usedIOS = self.hwControl.getUsedIOS()
            self.sendNetworkMessage(cmd_used_io_list[0]+f":{self.name}:{usedIOS}")

        elif str(msgParts[0]) == cmd_add_output[0]:
            self.checkMessage(msgParts, cmd_add_output)
            self.hwControl.newOutput(msgParts[1],int(msgParts[2]))
            #TODO remember output here in database

        elif str(msgParts[0]) == cmd_set_output[0]:
            self.checkMessage(msgParts, cmd_set_output)
            self.hwControl.setOutput(msgParts[1])

        elif str(msgParts[0]) == cmd_reset_outptut[0]:
            self.checkMessage(msgParts, cmd_reset_outptut)
            self.hwControl.resetOutput(msgParts[0])

        else:
            raise ValueError(f"Kommando {msgParts[0]} not known to client!")


    def sendNetworkMessage(self,msg):
        reactor.callFromThread(self.nwClient.sendMessage, msg)

    def checkMessage(self,msgParts,cmd):
        if len(msgParts) is not cmd[1]:
            raise ValueError(
                f"Length of message does not correspond to expected mesagelength. Message is {msgParts}, with "
                f"length {len(msgParts)}. Expected command is {cmd[0]} with expected length {cmd[1]}.")

