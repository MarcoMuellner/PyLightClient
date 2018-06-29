from django.core.exceptions import ObjectDoesNotExist
from hardware import GPIOControl

from PyLightCommon.cmdHandler.cmdHandler import cmd
from PyLightCommon.pylightcommon.models import ClientSettings


def changeIOOut(name,active):
    active = bool(active)
    if active:
        GPIOControl.inst().setOutput(name)
    elif not active:
        GPIOControl.inst().resetOutput(name)

@cmd
def addNewIO(name,io):
    GPIOControl.inst().newOutput(name,io)

@cmd
def changeSystemName(name):
    try:
        settings = ClientSettings.objects.get(pk=1)
    except ObjectDoesNotExist:
        settings = ClientSettings()
    settings.name = name
    settings.save()