from PyLightORM.models import UsedIOs,ClientSettings,IOs,IOTypes
from Support import Singleton

@Singleton
class DB:
    def getAllIOs(self):
        return list(IOs.objects.all().values_list('ioNr',flat=True))[1:]

    def getAllIOTypes(self):
        return list(IOTypes.objects.all().values_list('pk',flat=True))

    def getUsedIOs(self):
        usedIOs = {}
        for i in UsedIOs.objects.all():
            if i.pk ==0:
                continue
            usedIOs[i.name] = [i.pin_id,i.type_id,i.active]

        return usedIOs

    def addUsedIO(self, name, io, ioType):
        usedIOList = UsedIOs.objects.filter(name=name)
        if len(usedIOList) > 0:
            raise ValueError(f"An IO with name {name} is allready assigned. Allready assigned names "
                             f"are {list(UsedIOs.objects.all().values_list('name',flat=True))}")

        try:
            io = IOs.objects.filter(ioNr=io)[0]
        except IndexError:
            raise ValueError(f"No Pin available with nr {io}. Pins available are: {self.getAllIOs()}")

        try:
            ioType = IOTypes.objects.filter(pk=int(ioType))[0]
        except IndexError:
            raise ValueError(f"No IOType with type {ioType} available. Available types are {list(IOTypes.objects.all())}")

        newIO = UsedIOs(name=name,pin=io,type=ioType,active=False)
        newIO.save()

    def changeIOState(self,name,state):
        try:
            usedIO = UsedIOs.objects.filter(name=name)[0]
        except IndexError:
            raise ValueError(f"There is no IO assigned with name {name}. Allready assigned names "
                             f"are {list(UsedIOs.objects.all().values_list('name',flat=True))}")

        usedIO.active = state
        usedIO.save()

    def getIOState(self,name):
        try:
            usedIO = UsedIOs.objects.filter(name=name)[0]
        except IndexError:
            raise ValueError(f"There is no IO assigned with name {name}. Allready assigned names "
                             f"are {list(UsedIOs.objects.all().values_list('name',flat=True))}")

        return usedIO.active


    def getPinName(self,io):
        try:
            io = IOs.objects.filter(ioNr=io)[0]
        except IndexError:
            raise ValueError(f"No Pin available with nr {io}. Pins available are: {self.getAllIOs()}")

        try:
            usedIO = UsedIOs.objects.filter(pin=io)[0]
        except IndexError:
            raise ValueError(f"There is no IO assigned with pin {io}. Allready assigned names "
                             f"are {list(UsedIOs.objects.all().values_list('pin',flat=True))}")

        return usedIO.name

    def setPiName(self,name):
        try:
            settings = ClientSettings.objects.filter(pk=1)[0]
        except IndexError:
            settings = ClientSettings(pk=1)

        settings.clientName = name
        settings.save()

    def getPiName(self):
        try:
            settings = ClientSettings.objects.filter(pk=1)[0]
        except IndexError:
            settings = ClientSettings.objects.filter(pk=0)[0]

        return settings.clientName

    def getServerAddress(self):
        try:
            settings = ClientSettings.objects.filter(pk=1)[0]
        except IndexError:
            settings = ClientSettings.objects.filter(pk=0)[0]

        return settings.serverAddress

    def setServerAddress(self,address):
        try:
            settings = ClientSettings.objects.filter(pk=1)[0]
        except IndexError:
            settings = ClientSettings(pk=1)

        settings.serverAddress = address
        settings.save()