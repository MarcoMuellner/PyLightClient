import sys
from enum import Enum


class IOType(Enum):
    NONE = "IOType.NONE"
    OUTPUT =  "IOType.OUTPUT"
    INPUT = "IOType.INPUT"

try:
    from django.db import models
except  Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

class IOs(models.Model):
    ioNr = models.IntegerField(primary_key=True,verbose_name='physical io nr on pi')

class IOTypes(models.Model):
    ioType = models.CharField(max_length=255,choices=[(tag,tag.value) for tag in IOType],verbose_name="Type of output")

class UsedIOs(models.Model):
    name = models.CharField(max_length=255,verbose_name='human readable name for the io',unique=True)
    pin = models.OneToOneField(IOs,on_delete=models.CASCADE,verbose_name='Pin nr')
    type = models.ForeignKey(IOTypes,on_delete=models.CASCADE,verbose_name='Type of IO')
    active = models.BooleanField(default=False,verbose_name="Active/Non Active IO")

class ClientSettings(models.Model):
    clientName = models.CharField(max_length=255,verbose_name='Name of the pi client',default="")
    serverAddress = models.CharField(max_length=255,verbose_name='Address of the server that set the ip of the pi',default="")
