from huey import crontab
from django.core.exceptions import ObjectDoesNotExist
import requests
from requests.exceptions import InvalidURL,ConnectTimeout,ConnectionError
import logging

from PyLightClient.settings import huey
from control.Network import getServer
from PyLightCommon.pylightcommon.models import ClientSettings
from PyLightCommon.Commandos import *
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
        response = requests.get(f"http://{settings.serverAddress}:8000/hardwareRequest",params={"cmd":cmd_alive[0]},timeout=1)
        if response.status_code == 200 and response.text == cmd_ok[0]:
            logger.debug(f"Connection alive with server {settings.serverAddress}")
            return
    except (InvalidURL, ConnectTimeout, ConnectionError):
        logger.debug(f"Request not possible with url {settings.serverAddress}")
    rereadServer()


def rereadServer():
    try:
        settings = ClientSettings.objects.get(pk=1)
    except ObjectDoesNotExist:
        settings = ClientSettings()
        settings.save()


    logger.info("Client not connected to server, trying to find a new one")
    serverIP = getServer('127.0.0.1')
    logger.info(f"Found server at {serverIP}")
    logger.info(f"Connected to {serverIP}")

    requests.post(f"http://{serverIP}:8000/hardwareRequest/", data={"cmd": f"{cmd_signup[0]}||{settings.name}"
                                                                           f"||{GPIOControl.inst().allIOs}"
                                                                           f"||{GPIOControl.inst().getUsedIOS()}"})
    settings.serverAddress = serverIP
    settings.connectedToServer = True
    settings.save()





