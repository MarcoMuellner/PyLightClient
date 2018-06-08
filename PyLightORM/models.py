import sys

try:
    from django.db import models
except  Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()


class UsedIOs(models.Model):
    name = models.CharField(max_length=255,verbose_name='human readable name for the io')
    active = models.BooleanField(default=False,verbose_name="Active/Non Active IO")

class IOs(models.Model):
    ioNr = models.IntegerField(primary_key=True,verbose_name='physical io nr on pi')
    usedIOId = models.OneToOneField(UsedIOs,on_delete=models.CASCADE,verbose_name='link to the used ios')

class Client_settings(models.Model):
    clientName = models.CharField(max_length=255,verbose_name='Name of the pi client')
    serverAddress = models.CharField(max_length=255,verbose_name='Address of the server that set the ip of the pi')
