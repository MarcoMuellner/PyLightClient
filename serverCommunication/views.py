from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from PyLightCommon.Commandos import *
from PyLightCommon.pylightcommon.models import *
from hardware.GPIOControl import GPIOControl

# Create your views here.

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ServerCommunication(View):
    @csrf_exempt
    def get(self,request):
        pass

    def post(self,request):
        data = request.POST["cmd"].split("||")
        logger.info(f"Received data: {data}")
        if data[0] == cmd_change_name[0]:
            logger.info(f"Changing name to {data[1]}")
            settings = ClientSettings.objects.get(pk=1)
            settings.name = data[1]
            settings.save()
        elif data[0] == cmd_add_output[0]:
            logger.info(f"New ouptut with name {data[1]}")
            GPIOControl.inst().newOutput(data[1],int(data[2]))
        elif data[0] == cmd_set_output[0]:
            logger.info(f"Setting output with name {data[1]}")
            GPIOControl.inst().setOutput(data[1])
        elif data[0] == cmd_reset_outptut[0]:
            logger.info(f"Resetting output with name {data[1]}")
            GPIOControl.inst().resetOutput(data[1])
        
        return HttpResponse("Ok",content_type="text/plain")
