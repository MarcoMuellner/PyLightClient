import pytest
from PyLightControl.Database import DB
from PyLightORM.models import UsedIOs,ClientSettings,IOs,IOTypes,IOType

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

def testGetAllIOs():
    assert len(DB.inst().getAllIOs()) == len(IOs.objects.all())-1

def testGetAllIOTypes():
    assert len(DB.inst().getAllIOTypes()) == len(IOTypes.objects.all()) -1

def testGetUsedIOs():
    assert len(DB.inst().getUsedIOs()) == len(UsedIOs.objects.all()) -1
    io = IOs.objects.filter(ioNr=3)[0]
    ioType = IOTypes.objects.filter(pk=1)[0]
    newIO = UsedIOs(name="test",pin=io,type=ioType,active=False)
    newIO.save()
    assert len(DB.inst().getUsedIOs()) == len(UsedIOs.objects.all()) - 1

def testAddUsedIO():
    for i in DB.inst().getAllIOs():
        DB.inst().addUsedIO(f"test{i}",i,IOType.OUTPUT)

    assert len(DB.inst().getUsedIOs()) == len(DB.inst().getAllIOs())

def testAddUsedIOFailed():
    with pytest.raises(ValueError):
        DB.inst().addUsedIO(f"test", 100, IOType.OUTPUT)

    with pytest.raises(ValueError):
        DB.inst().addUsedIO(f"test", 3, -1)

    DB.inst().addUsedIO(f"test", 3, IOType.OUTPUT)

    with pytest.raises(ValueError):
        DB.inst().addUsedIO(f"test", 3, IOType.OUTPUT)

    with pytest.raises(ValueError):
        DB.inst().addUsedIO(f"test", 4, IOType.OUTPUT)


def testChangeIOState():
    DB.inst().addUsedIO(f"test", 3, IOType.OUTPUT)
    assert UsedIOs.objects.filter(name=f"test")[0].active == False
    DB.inst().changeIOState(f"test",True)
    assert UsedIOs.objects.filter(name=f"test")[0].active == True

def testGetIOState():
    DB.inst().addUsedIO(f"test", 3, IOType.OUTPUT)
    assert DB.inst().getIOState(f"test") == False
    DB.inst().changeIOState(f"test", True)
    assert DB.inst().getIOState(f"test") == True

def testGetPinName():
    DB.inst().addUsedIO(f"test", 3, IOType.OUTPUT)
    assert UsedIOs.objects.filter(name=f"test")[0].pin_id == 3
    assert DB.inst().getPinName(3) == f"test"

    with pytest.raises(ValueError):
        DB.inst().getPinName(100)

    with pytest.raises(ValueError):
        DB.inst().getPinName(5)

def testSetPiName():
    DB.inst().setPiName("Hello_Pi")
    assert ClientSettings.objects.filter(pk=1)[0].clientName == "Hello_Pi"
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
    assert ClientSettings.objects.filter(pk=1)[0].clientName == ""
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
    DB.inst().addUsedIO(f"test", 3, IOType.OUTPUT)
    assert len(DB.inst().getUsedIOPinNr()) == 1
    assert 3 in DB.inst().getUsedIOPinNr()

def testRemoveUsedIO():
    assert len(DB.inst().getUsedIOs()) == 0
    DB.inst().addUsedIO(f"test", 3, IOType.OUTPUT)
    assert len(DB.inst().getUsedIOs()) == 1
    DB.inst().removeUsedIO(f"test")
    assert len(DB.inst().getUsedIOs()) == 0

def testRemoveAllUsedIO():
    assert len(DB.inst().getUsedIOs()) == 0
    for i in DB.inst().getAllIOs():
        DB.inst().addUsedIO(f"test{i}",i,IOType.OUTPUT)

    assert len(DB.inst().getUsedIOs()) == len(DB.inst().getAllIOs())

    DB.inst().removeAllUsedIO()

    assert len(DB.inst().getUsedIOs()) == 0






