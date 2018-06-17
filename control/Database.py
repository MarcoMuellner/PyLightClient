from PyLightCommon.pylightcommon.models import UsedIO,ClientSettings,IO,IOType,EnumIOType
from django.core.exceptions import ObjectDoesNotExist
from PyLightCommon import Singleton

@Singleton
class DB:
    def getAllIO(self):
        return list(IO.objects.exclude(pk=0).values_list('ioNr',flat=True))

    def getAllIOType(self):
        typeList = []
        for i in IOType.objects.exclude(pk=0).values_list('ioType'):
            typeList.append(EnumIOType(i[0]))
        return typeList

    def getUsedIO(self):
        usedIODict = {}
        for i in UsedIO.objects.all():
            usedIODict[i.name] = [i.pin_id, EnumIOType(i.type.ioType), i.active]

        return usedIODict

    def getUsedIOPinNr(self):
        return list(UsedIO.objects.all().values_list('pin_id',flat=True))

    def addUsedIO(self, name, io, ioType: EnumIOType):
        UsedIO.objects.filter(name=name).delete()

        try:
            io = IO.objects.get(ioNr=io)
        except ObjectDoesNotExist:
            raise ValueError(f"No Pin available with nr {io}. Pins available are: {self.getAllIO()}")

        try:
            ioTypus = IOType.objects.get(ioType=ioType.value)
        except ObjectDoesNotExist:
            raise ValueError(f"No IOType with type {ioType} available. Available types are {list(IOType.objects.all())}")
        except AttributeError:
            raise ValueError(
                f"IOType {ioType} is no correct IO Type.")

        newIO = UsedIO(name=name,pin=io,type=ioTypus,active=False)
        newIO.save()

    def removeUsedIO(self,name):
        UsedIO.objects.filter(name=name).delete()

    def removeAllUsedIO(self):
        UsedIO.objects.exclude(pk=0).delete()


    def changeIOState(self,name,state):
        try:
            usedIO = UsedIO.objects.get(name=name)
        except ObjectDoesNotExist:
            raise ValueError(f"There is no IO assigned with name {name}. Allready assigned names "
                             f"are {list(UsedIO.objects.all().values_list('name',flat=True))}")

        usedIO.active = state
        usedIO.save()

    def getIOState(self,name):
        try:
            usedIO = UsedIO.objects.get(name=name)
        except ObjectDoesNotExist:
            raise ValueError(f"There is no IO assigned with name {name}. Allready assigned names "
                             f"are {list(UsedIO.objects.all().values_list('name',flat=True))}")

        return usedIO.active


    def getPinName(self,io):
        try:
            io = IO.objects.get(ioNr=io)
        except ObjectDoesNotExist:
            raise ValueError(f"No Pin available with nr {io}. Pins available are: {self.getAllIO()}")

        try:
            usedIO = UsedIO.objects.get(pin=io)
        except ObjectDoesNotExist:
            raise ValueError(f"There is no IO assigned with pin {io}. Allready assigned names "
                             f"are {list(UsedIO.objects.all().values_list('pin',flat=True))}")

        return usedIO.name

    def setPiName(self,name):
        try:
            settings = ClientSettings.objects.get(pk=1)
        except ObjectDoesNotExist:
            settings = ClientSettings(pk=1)

        settings.name = name
        settings.save()

    def getPiName(self):
        try:
            settings = ClientSettings.objects.get(pk=1)
        except ObjectDoesNotExist:
            settings = self.setupDefaultSettings()

        return settings.name

    def getServerAddress(self):
        try:
            settings = ClientSettings.objects.get(pk=1)
        except ObjectDoesNotExist:
            settings = ClientSettings(pk=0)
            settings.save()

        return settings.serverAddress

    def setServerAddress(self,address):
        try:
            settings = ClientSettings.objects.get(pk=1)
        except ObjectDoesNotExist:
            settings = ClientSettings(pk=1)

        settings.serverAddress = address
        settings.save()

    def setupDefaultSettings(self):
        settings = ClientSettings(pk=0)
        settings.save()
        return settings