import pytest
from PyLightControl.Database import DB
from PyLightCommon.pylightcommon.models import UsedIO,ClientSettings,IO,IOType,EnumIOType

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

def testGetAllIO():
    assert len(DB.inst().getAllIO()) == len(IO.objects.all()) - 1

def testGetAllIOType():
    assert len(DB.inst().getAllIOType()) == len(IOType.objects.all()) - 1

def testGetUsedIO():
    assert len(DB.inst().getUsedIO()) == len(UsedIO.objects.all())
    io = IO.objects.filter(ioNr=3)[0]
    ioType = IOType.objects.filter(pk=1)[0]
    newIO = UsedIO(name="test",pin=io,type=ioType,active=False)
    newIO.save()
    assert len(DB.inst().getUsedIO()) == len(UsedIO.objects.all())

def testAddUsedIO():
    for i in DB.inst().getAllIO():
        DB.inst().addUsedIO(f"test{i}",i,EnumIOType.OUTPUT)

    assert len(DB.inst().getUsedIO()) == len(DB.inst().getAllIO())

def testAddUsedIOFailed():
    with pytest.raises(ValueError):
        DB.inst().addUsedIO(f"test", 100, EnumIOType.OUTPUT)

    with pytest.raises(ValueError):
        DB.inst().addUsedIO(f"test", 3, -1)

    DB.inst().addUsedIO(f"test", 3, EnumIOType.OUTPUT)

    with pytest.raises(ValueError):
        DB.inst().addUsedIO(f"test", 3, EnumIOType.OUTPUT)

    with pytest.raises(ValueError):
        DB.inst().addUsedIO(f"test", 4, EnumIOType.OUTPUT)


def testChangeIOState():
    DB.inst().addUsedIO(f"test", 3, EnumIOType.OUTPUT)
    assert UsedIO.objects.filter(name=f"test")[0].active == False
    DB.inst().changeIOState(f"test",True)
    assert UsedIO.objects.filter(name=f"test")[0].active == True

def testGetIOState():
    DB.inst().addUsedIO(f"test", 3, EnumIOType.OUTPUT)
    assert DB.inst().getIOState(f"test") == False
    DB.inst().changeIOState(f"test", True)
    assert DB.inst().getIOState(f"test") == True

def testGetPinName():
    DB.inst().addUsedIO(f"test", 3, EnumIOType.OUTPUT)
    assert UsedIO.objects.filter(name=f"test")[0].pin_id == 3
    assert DB.inst().getPinName(3) == f"test"

    with pytest.raises(ValueError):
        DB.inst().getPinName(100)

    with pytest.raises(ValueError):
        DB.inst().getPinName(5)

def testSetPiName():
    DB.inst().setPiName("Hello_Pi")
    assert ClientSettings.objects.filter(pk=1)[0].name == "Hello_Pi"
    assert ClientSettings.objects.filter(pk=1)[0].serverAddress == ""

def testGetPiName():
    assert DB.inst().getPiName() == ""
    DB.inst().setPiName("Hello_Pi")
    assert DB.inst().getPiName() == "Hello_Pi"
    assert len(ClientSettings.objects.all()) == 2
    DB.inst().setPiName("Hello_Pi2")
    assert DB.inst().getPiName() == "Hello_Pi2"
    assert len(ClientSettings.objects.all()) == 2

def testSetServerAddress():
    DB.inst().setServerAddress('127.0.0.1')
    assert ClientSettings.objects.filter(pk=1)[0].name == ""
    assert ClientSettings.objects.filter(pk=1)[0].serverAddress == "127.0.0.1"

def testGetServerAddress():
    assert DB.inst().getServerAddress() == ""
    DB.inst().setServerAddress("127.0.0.1")
    assert DB.inst().getServerAddress() == "127.0.0.1"
    assert len(ClientSettings.objects.all()) == 2
    DB.inst().setServerAddress("127.0.0.2")
    assert DB.inst().getServerAddress() == "127.0.0.2"
    assert len(ClientSettings.objects.all()) == 2

def testGetUsedIOPinNr():
    assert len(DB.inst().getUsedIOPinNr()) == 0
    DB.inst().addUsedIO(f"test", 3, EnumIOType.OUTPUT)
    assert len(DB.inst().getUsedIOPinNr()) == 1
    assert 3 in DB.inst().getUsedIOPinNr()

def testRemoveUsedIO():
    assert len(DB.inst().getUsedIO()) == 0
    DB.inst().addUsedIO(f"test", 3, EnumIOType.OUTPUT)
    assert len(DB.inst().getUsedIO()) == 1
    DB.inst().removeUsedIO(f"test")
    assert len(DB.inst().getUsedIO()) == 0

def testRemoveAllUsedIO():
    assert len(DB.inst().getUsedIO()) == 0
    for i in DB.inst().getAllIO():
        DB.inst().addUsedIO(f"test{i}",i,EnumIOType.OUTPUT)

    assert len(DB.inst().getUsedIO()) == len(DB.inst().getAllIO())

    DB.inst().removeAllUsedIO()

    assert len(DB.inst().getUsedIO()) == 0






