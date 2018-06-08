try:
    import RPi.GPIO as GPIO
    piHW = True
except Exception as e:
    print("Error import RPi. Assuming to be on a non Pi Hardware!")
    print(e)
    print("Setting Hardware to False")
    piHW = False

from PyLightControl.Database import DB
from PyLightORM.models import IOType


class GPIOControl:
    """
    GPIOControl allows for a central point of controlling the IOs on the Pi. Access the IOs through custom names 
    for each output (preferably defined via the  Web interface).     
    """
    def __init__(self,resetFlag: bool):
        """
        Sets up the Board, creates lists for available pins
        """
        if piHW:
            GPIO.setmode(GPIO.BOARD)
        #Defines the "Unused" pins
        self.allIOs = DB.inst().getAllIOs()
        if resetFlag:
            self._openIOs = self.allIOs[:]
            self._usedIOs = {}
            DB.inst().removeAllUsedIO()
        else:
            self._usedIOs = DB.inst().getUsedIOs()
            self._openIOs = self.allIOs[:]
            self._openIOs.remove(DB.inst().getUsedIOPinNr)
            for i in self._usedIOs:
                if i.type == IOType.OUTPUT:
                    self.setOutputState(i.name,i.active)

    def newOutput(self, name: str, pin: int) -> bool:
        """
        Adds a new output controlled by GPIOControl. Afterwards it is accessible only via its name. Convinience Function
        :param name: Human readable name for the Output.
        :param pin: Pin number that should be used
        :return: True if output was added successfully. False if not
        """
        return self.newIO(IOType.OUTPUT,name,pin)

    def newInput(self, name: str, pin: int) -> bool:
        """
        Adds a new input controlled by GPIOControl. Afterwards it is accessible only via its name. Convinience Function
        :param name: Human readable name for the Input
        :param pin: Pin number that should be used
        :return: True if input was added successfully. False if not
        """
        return self.newIO(IOType.INPUT,name,pin)

    def newIO(self, ioType: IOType, name: str, pin: int) -> bool:
        """
        Adds a new IO to be controlled by GPIOControl. Afterwards it is accessible only via its name through the
        accesser functions. 
        :param ioType: Type of the IO. Must be Enum of Type IOType
        :param name: Human readable name for the IO
        :param pin: Pin number that should be used
        :return: True if input was added successfully, False if not
        """
        if not isinstance(ioType,IOType):
            raise TypeError("ioType must be of IOType enum!")

        if pin not in self.allIOs:
            raise ValueError(f"Pin {pin} is not in the available IOs!")

        if pin not in self._openIOs:
            self.removeIO(pin)

        if piHW:
            if ioType is IOType.OUTPUT:
                GPIO.setup(pin,GPIO.OUT,initial=False)
                self._usedIOs[name] = [pin, ioType, False]
            elif ioType is IOType.INPUT:
                GPIO.setup(pin,GPIO.IN)
                self._usedIOs[name] = [pin, ioType]
        else:
            if ioType is IOType.OUTPUT:
                self._usedIOs[name] = [pin, ioType, False]
            elif ioType is IOType.INPUT:
                self._usedIOs[name] = [pin, ioType]

        self._openIOs.remove(pin)

        if ioType not in DB.inst().getAllIOTypes():
            raise ValueError(f"IOType is not Output nor input! Probably something that is not yet implemented? "
                             f"Type is {ioType}. Available is {DB.inst().getAllIOTypes()}")
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
        if self._usedIOs[name][1] == IOType.OUTPUT:
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