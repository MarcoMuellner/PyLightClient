from PyLightORM.models import UsedIOs,ClientSettings,IOs,IOTypes,IOType
from django.core.exceptions import ObjectDoesNotExist
from Support import Singleton

@Singleton
class DB:
    def getAllIOs(self):
        return list(IOs.objects.exclude(pk=0).values_list('ioNr',flat=True))

    def getAllIOTypes(self):
        typeList = []
        for i in IOTypes.objects.exclude(pk=0).values_list('ioType'):
            typeList.append(IOType(i[0]))
        return typeList

    def getUsedIOs(self):
        usedIOs = {}
        for i in UsedIOs.objects.all():
            if i.pk ==0:
                continue
            usedIOs[i.name] = [i.pin_id,IOType(i.type.ioType),i.active]

        return usedIOs

    def getUsedIOPinNr(self):
        return list(UsedIOs.objects.all().values_list('pin_id',flat=True))[1:]

    def addUsedIO(self, name, io, ioType):
        usedIOList = UsedIOs.objects.filter(name=name)
        if len(usedIOList) > 0:
            raise ValueError(f"An IO with name {name} is allready assigned. Allready assigned names "
                             f"are {list(UsedIOs.objects.all().values_list('name',flat=True))}")

        try:
            io = IOs.objects.get(ioNr=io)
        except ObjectDoesNotExist:
            raise ValueError(f"No Pin available with nr {io}. Pins available are: {self.getAllIOs()}")

        try:
            ioTypus = IOTypes.objects.get(ioType=ioType)
        except ObjectDoesNotExist:
            raise ValueError(f"No IOType with type {ioType} available. Available types are {list(IOTypes.objects.all())}")

        newIO = UsedIOs(name=name,pin=io,type=ioTypus,active=False)
        newIO.save()

    def removeUsedIO(self,name):
        UsedIOs.objects.filter(name=name).delete()

    def removeAllUsedIO(self):
        UsedIOs.objects.exclude(pk=0).delete()


    def changeIOState(self,name,state):
        try:
            usedIO = UsedIOs.objects.get(name=name)
        except ObjectDoesNotExist:
            raise ValueError(f"There is no IO assigned with name {name}. Allready assigned names "
                             f"are {list(UsedIOs.objects.all().values_list('name',flat=True))}")

        usedIO.active = state
        usedIO.save()

    def getIOState(self,name):
        try:
            usedIO = UsedIOs.objects.get(name=name)
        except ObjectDoesNotExist:
            raise ValueError(f"There is no IO assigned with name {name}. Allready assigned names "
                             f"are {list(UsedIOs.objects.all().values_list('name',flat=True))}")

        return usedIO.active


    def getPinName(self,io):
        try:
            io = IOs.objects.get(ioNr=io)
        except ObjectDoesNotExist:
            raise ValueError(f"No Pin available with nr {io}. Pins available are: {self.getAllIOs()}")

        try:
            usedIO = UsedIOs.objects.get(pin=io)
        except ObjectDoesNotExist:
            raise ValueError(f"There is no IO assigned with pin {io}. Allready assigned names "
                             f"are {list(UsedIOs.objects.all().values_list('pin',flat=True))}")

        return usedIO.name

    def setPiName(self,name):
        try:
            settings = ClientSettings.objects.get(pk=1)
        except ObjectDoesNotExist:
            settings = ClientSettings(pk=1)

        settings.clientName = name
        settings.save()

    def getPiName(self):
        try:
            settings = ClientSettings.objects.get(pk=1)
        except ObjectDoesNotExist:
            settings = ClientSettings.objects.get(pk=0)

        return settings.clientName

    def getServerAddress(self):
        try:
            settings = ClientSettings.objects.get(pk=1)
        except ObjectDoesNotExist:
            settings = ClientSettings.objects.get(pk=0)

        return settings.serverAddress

    def setServerAddress(self,address):
        try:
            settings = ClientSettings.objects.get(pk=1)
        except ObjectDoesNotExist:
            settings = ClientSettings(pk=1)

        settings.serverAddress = address
        settings.save()