try:
    import RPi.GPIO as GPIO
    piHW = True
except Exception as e:
    print("Error import RPi. Assuming to be on a non Pi Hardware!")
    print(e)
    print("Setting Hardware to False")
    piHW = False

from control.Database import DB
from PyLightCommon.pylightcommon.models import EnumIOType
from PyLightCommon import Singleton

@Singleton
class GPIOControl:
    """
    GPIOControl allows for a central point of controlling the IOs on the Pi. Access the IOs through custom names 
    for each output (preferably defined via the  Web interface).     
    """
    def __init__(self):
        """
        Sets up the Board, creates lists for available pins
        """
        if piHW:
            GPIO.setmode(GPIO.BOARD)
        #Defines the "Unused" pins
        self.allIOs = DB.inst().getAllIO()
        self._usedIOs = DB.inst().getUsedIO()
        self._openIOs = [x for x in self.allIOs if x not in DB.inst().getUsedIOPinNr()]
        DB.inst().removeAllUsedIO()

    def newOutput(self, name: str, pin: int) -> bool:
        """
        Adds a new output controlled by GPIOControl. Afterwards it is accessible only via its name. Convinience Function
        :param name: Human readable name for the Output.
        :param pin: Pin number that should be used
        :return: True if output was added successfully. False if not
        """
        return self.newIO(EnumIOType.OUTPUT,name,pin)

    def newInput(self, name: str, pin: int) -> bool:
        """
        Adds a new input controlled by GPIOControl. Afterwards it is accessible only via its name. Convinience Function
        :param name: Human readable name for the Input
        :param pin: Pin number that should be used
        :return: True if input was added successfully. False if not
        """
        return self.newIO(EnumIOType.INPUT,name,pin)

    def newIO(self, ioType: EnumIOType, name: str, pin: int) -> bool:
        """
        Adds a new IO to be controlled by GPIOControl. Afterwards it is accessible only via its name through the
        accesser functions. 
        :param ioType: Type of the IO. Must be Enum of Type EnumIOType
        :param name: Human readable name for the IO
        :param pin: Pin number that should be used
        :return: True if input was added successfully, False if not
        """
        pin = int(pin)
        if not isinstance(ioType,EnumIOType):
            raise TypeError("EnumIOType must be of EnumIOType enum!")

        if pin not in self.allIOs:
            raise ValueError(f"Pin {pin} is not in the available IOs!")

        if pin not in self._openIOs:
            self.removeIO(pin)

        if piHW:
            if ioType is EnumIOType.OUTPUT:
                GPIO.setup(pin,GPIO.OUT,initial=False)
                self._usedIOs[name] = [pin, EnumIOType.OUTPUT, False]
            elif ioType is EnumIOType.INPUT:
                GPIO.setup(pin,GPIO.IN)
                self._usedIOs[name] = [pin, EnumIOType.INPUT]
        else:
            if ioType is EnumIOType.OUTPUT:
                self._usedIOs[name] = [pin, EnumIOType.OUTPUT, False]
            elif ioType is EnumIOType.INPUT:
                self._usedIOs[name] = [pin, EnumIOType.INPUT]

        self._openIOs.remove(pin)

        if ioType not in DB.inst().getAllIOType():
            raise ValueError(f"EnumIOType is not Output nor input! Probably something that is not yet implemented? "
                             f"Type is {EnumIOType}. Available is {DB.inst().getAllIOType()}")
        DB.inst().addUsedIO(name,pin,ioType)
        return True


    def removeIO(self, pin: int):
        """
        Removes an IO from the internal dict and frees its pin.
        :param pin: Pin number that should be used
        """
        try:
            for key,val in self._usedIOs.items():
                if pin is val[0]:
                    name=key
                    break

            if name in self._usedIOs.keys():
                if piHW:
                    GPIO.cleanup(self._usedIOs[name][0])
                self._openIOs.append(self._usedIOs[name][0])
                del self._usedIOs[name]
        except UnboundLocalError:
            return
        finally:
            try:
                DB.inst().removeUsedIO(DB.inst().getPinName(pin))
            except ValueError:
                pass


    def setOutput(self, name: str):
        """
        Sets an Output to True. Must be added beforehand using newIO/newOutput. Convinience function.
        :param name: Human readable name, contained in dict
        """
        self.setOutputState(name,True)

    def resetOutput(self, name: str) -> bool:
        """
        Resets an Output to False. Must be added beforehand using newIO/newOutput. Convinience function.
        :param name: Human readable name, contained in dict
        :return: True if successful, False if not
        """
        self.setOutputState(name,False)

    def setOutputState(self, name: str, state: bool) -> bool:
        """
        Sets an output to a certain state.
        :param name: Human readable name,contained in dict
        :param state: State to set to
        :return: True if successful, False if not.
        """
        if self._usedIOs[name][1] == EnumIOType.OUTPUT:
            if piHW:
                GPIO.output(self._usedIOs[name][0], state)
            self._usedIOs[name][2] = state
            DB.inst().changeIOState(name,state)
        else:
            print(self._usedIOs)
            raise TypeError(f"We can only set and reset Outputs! IO {name} is type {self._usedIOs[name][1]}")


    def getIOState(self, name: str) -> bool:
        """
        Returns the state of a given output with name.
        :param name: Human readable name of the output
        :return: True if state true, else false
        """
        if piHW:
            return GPIO.input(self._usedIOs[name][0])
        else:
            return self._usedIOs[name][2]

    def getOpenIOS(self) -> list:
        """
        :return: Returns the list of all open IOs
        """
        return self._openIOs

    def getUsedIOS(self):
        """
        :return: Returns dict of all used IOS, containing names and current state
        """
        return self._usedIOs

    def getserial(self):
        # Extract serial from cpuinfo file
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"

        return cpuserial