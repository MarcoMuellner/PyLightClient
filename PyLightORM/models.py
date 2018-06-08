import sys

try:
    from django.db import models
except  Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

class IOs(models.Model):
    ioNr = models.IntegerField(primary_key=True,verbose_name='physical io nr on pi')

class IOTypes(models.Model):
    name = models.CharField(max_length=255,verbose_name="Name of the output")

class UsedIOs(models.Model):
    name = models.CharField(max_length=255,verbose_name='human readable name for the io')
    pin = models.OneToOneField(IOs,on_delete=models.CASCADE,verbose_name='Pin nr')
    type = models.ForeignKey(IOTypes,on_delete=models.CASCADE,verbose_name='Type of IO')
    active = models.BooleanField(default=False,verbose_name="Active/Non Active IO")

class ClientSettings(models.Model):
    clientName = models.CharField(max_length=255,verbose_name='Name of the pi client')
    serverAddress = models.CharField(max_length=255,verbose_name='Address of the server that set the ip of the pi')
