from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
from queue import Queue,Empty
import signal
import sys

from PyLightHardware import GPIOControl
from PyLightControl.Network import NetworkClient
from PyLightControl.Database import DB
from PyLightCommon.Globals import *
from PyLightCommon.Commandos import *

import time



class Controller:
    """
    The Controller class provides a central entry point to PyLightClient. It starts the network procedures, reads
    all IOs from HW Control, and spawns the necessary threads and/or processes. It also handles all incoming commands
    and performs the actions according to the command. See Commandos file for all commands

    The general procedure is this:
    - Get all IOs
    - Find Server with NetworkClient
    - spawn worker and network thread

    Communication between Network and worker happens using a queue. The Control unit registers this instance as
    an interested party to the network communication, which in turn will put the commandos in the queue. It then will
    work of each command of the queue sequentially.
    """
    def __init__(self):
        """
        The Constructor sets up Hardware, DB and Network. It then starts all processes. For the constructors of
        Network, Hardware and DB see each according class
        """
        oldIp = DB.inst().getServerAddress()
        self.nwClient = NetworkClient(port,oldIp)
        self.resetFlag = False
        self.killFlag = False
        if oldIp != self.nwClient.server_addres:
            self.resetFlag = True
            DB.inst().setServerAddress(self.nwClient.server_addres)

        self.hwControl = GPIOControl(self.resetFlag)

        self.queue = Queue()
        signal.signal(signal.SIGINT, self.signal_handler)
        self.startProcesses()

    def startProcesses(self):
        """
        Registers the instance to the network client, creates an TCP4 Endpoint and runs the worker thread as well
        as the reactor thread
        """
        self.nwClient.registerProces(self)
        point = TCP4ClientEndpoint(reactor,self.nwClient.server_addres,port)
        connectProtocol(point,self.nwClient)
        reactor.callInThread(self.worker)
        reactor.run()

    def worker(self):
        """
        This is the worker thread. It waits for incoming queue commandos and works them off sequentially.
        """
        print("STARTING COMMAND LOOP!")
        while True:
            try:
                message = self.queue.get(timeout=1)
                self.parse_message(message)
            except Empty:
                pass
            if self.killFlag:
                break


    def setupHardware(self):
        #TODO read all old states from database, and set them accordingly
        pass

    def put_message(self,msg):
        self.queue.put(msg)

    def parse_message(self,msg:bytes):
        """
        Parses Network commandos from Commando and performs actions. It also checks if the commando has the expected
        length.
        :param msg: Network message
        """
        msgParts = msg.decode().split("||")

        if str(msgParts[0]) == cmd_welcome[0]:
            self.checkMessage(msgParts,cmd_welcome)
            self.name = msgParts[1]
            DB.inst().setPiName(self.name)

            allIOS = self.hwControl.allIOs
            self.sendNetworkMessage(cmd_all_io_list[0]+f"||{self.name}||{allIOS}")
            usedIOS = self.hwControl.getUsedIOS()
            self.sendNetworkMessage(cmd_used_io_list[0]+f"||{self.name}||{usedIOS}")

        elif str(msgParts[0]) == cmd_add_output[0]:
            self.checkMessage(msgParts, cmd_add_output)
            self.hwControl.newOutput(msgParts[1],int(msgParts[2]))
            #TODO remember output here in database

        elif str(msgParts[0]) == cmd_set_output[0]:
            self.checkMessage(msgParts, cmd_set_output)
            self.hwControl.setOutput(msgParts[1])

        elif str(msgParts[0]) == cmd_reset_outptut[0]:
            self.checkMessage(msgParts, cmd_reset_outptut)
            self.hwControl.resetOutput(msgParts[1])

        elif str(msgParts[0]) == cmd_shutdown_now[0]:
            self.killFlag = True
            reactor.callFromThread(reactor.stop)

        elif str(msgParts[0]) == cmd_client_connected[0]:
            self.sendNetworkMessage(cmd_signup[0]+f"||{self.nwClient.ip}||{self.nwClient.macAddress}||{self.hwControl.getserial()}")

        elif str(msgParts[0]) == cmd_client_disconnected[0]:
            self.nwClient.runInitProces(port)
            point = TCP4ClientEndpoint(reactor, self.nwClient.server_addres, port)
            reactor.callFromThread(connectProtocol(point, self.nwClient))

        else:
            print(f"Kommando {msgParts[0]} not known to client!")


    def sendNetworkMessage(self,msg):
        reactor.callFromThread(self.nwClient.sendMessage, msg)

    def checkMessage(self,msgParts,cmd):
        if len(msgParts) is not cmd[1]:
            raise ValueError(
                f"Length of message does not correspond to expected mesagelength. Message is {msgParts}, with "
                f"length {len(msgParts)}. Expected command is {cmd[0]} with expected length {cmd[1]}.")

    def signal_handler(self,signal, handler):
        self.killFlag = True
        self.nwClient.killFlag = True
        reactor.callFromThread(reactor.stop)



