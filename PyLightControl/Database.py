from PyLightORM.models import UsedIOs,ClientSettings,IOs

class DB:
    def __init__(self):
        pass

    def getAllIOs(self):
        return list(IOs.objects.all().values_list('ioNr',flat=True))

    def addUsedIO(self,name,io):
        pass

    def changeIOState(self,name):
        pass

    def getIOSTate(self,name):
        pass

    def getUsedIOs(self):
        pass

    def getPiName(self):
        pass

    def setPiName(self):
        pass

    def getServerAddress(self):
        pass

    def setServerAddress(self):
        pass