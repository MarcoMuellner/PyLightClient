from huey import crontab
from django.core.exceptions import ObjectDoesNotExist
import requests
from requests.exceptions import InvalidURL,ConnectTimeout,ConnectionError
import logging

from PyLightClient.settings import huey
from control.Network import getServer
from PyLightCommon.pylightcommon.models import ClientSettings
from PyLightCommon.Commandos import *
from PyLightCommon.cmdHandler.cmdHandler import sendCommand
from hardware import GPIOControl


logger = logging.getLogger(__name__)

@huey.periodic_task(crontab(minute='*'))
@huey.lock_task('check-alive-lock')
def checkAlive():
    try:
        settings = ClientSettings.objects.get(pk=1)
    except ObjectDoesNotExist:
        settings = ClientSettings()
        settings.save()

    try:
        sendCommand(settings.serverAddress,
                    commando="Alive")
        return
    except (InvalidURL, ConnectTimeout, ConnectionError):
        logger.debug(f"Request not possible with url {settings.serverAddress}")
    rereadServer()


def rereadServer():
    logger.info("Client not connected to server, trying to find a new one")
    serverIP = getServer('127.0.0.1')
    logger.info(f"Found server at {serverIP}")
    logger.info(f"Connected to {serverIP}")

    sendCommand(serverIP,
                commando="Signup",
                lastIP = "127.0.0.1",
                serialNumber=GPIOControl.inst().getserial(),
                lastMac = "0x0x0x0x0x0",
                connected = True,
                active = True,
                )





