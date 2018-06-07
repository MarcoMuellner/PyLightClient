try:
    import RPi.GPIO as GPIO
    piHW = True
except Exception as e:
    print("Error import RPi. Assuming to be on a non Pi Hardware!")
    print(e)
    print("Setting Hardware to False")
    piHW = False

from enum import Enum

class IOType(Enum):
    OUTPUT = 1
    INPUT = 1


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
        self.allIOS = [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36, 37, 38]
        self._openIOs = self.allIOS[:]
        self._usedIOs = {}

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

        if pin not in self.allIOS:
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

        if ioType is not IOType.OUTPUT and ioType is not IOType.INPUT:
            raise ValueError(f"IOType is not Output nor input! Probably something that is not yet implemented? Type is {ioType}")

        return True


    def removeIO(self, pin: int):
        """
        Removes an IO from the internal dict and frees its pin. No longer accessible!
        :param ioType: Type of the IO. Must be Enum of Type IOType
        :param name: Human readable name for the IO
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
        if self._usedIOs[name][1] is IOType.OUTPUT:
            if piHW:
                GPIO.output(self._usedIOs[name][0], state)
            self._usedIOs[name][2] = state
        else:
            raise TypeError(f"We can only set and reset Outputs! IO {name} is type {self._usedIOs[name][2]}")


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