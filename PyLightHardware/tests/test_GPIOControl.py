import pytest
from PyLightHardware.GPIOControl import GPIOControl,IOType

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture(scope='module')
def moduleSetup(request):
    return GPIOControl(True)

@pytest.fixture(scope='function')
def functionSetup(request):
    return GPIOControl(True)

testCases = [("One",3,IOType.OUTPUT),
             ("Two",5,IOType.OUTPUT),
             (3,7,IOType.OUTPUT),
             (4.0,8,IOType.OUTPUT),
             ("Five",3,IOType.OUTPUT),
             ("Six", 10,IOType.INPUT),
             ("Seven", 11,IOType.INPUT),
             (8, 12,IOType.INPUT),
             (9.0, 13,IOType.INPUT),
             ("Ten", 10,IOType.INPUT)
             ]

@pytest.mark.parametrize("value",testCases)
def testNewOutput(moduleSetup: GPIOControl, value: list):
    if value[2] == IOType.OUTPUT:
        assert moduleSetup.newOutput(value[0],value[1])
        assert value[0] in moduleSetup._usedIOs.keys()
        assert value[1] not in moduleSetup._openIOs


@pytest.mark.parametrize("value",testCases)
def testNewInput(moduleSetup: GPIOControl, value: list):
    if value[2] == IOType.INPUT:
        assert moduleSetup.newInput(value[0],value[1])
        assert value[0] in moduleSetup._usedIOs.keys()
        assert value[1] not in moduleSetup._openIOs


@pytest.mark.parametrize("value",testCases)
def testNewIO(moduleSetup: GPIOControl, value: list):
    assert moduleSetup.newIO(value[2],value[0],value[1])
    assert value[0] in moduleSetup._usedIOs.keys()
    assert value[1] not in moduleSetup._openIOs


@pytest.mark.parametrize("value",testCases)
def testRemoveIO(moduleSetup: GPIOControl, value: list):
    moduleSetup.removeIO(value[1])
    assert value[0] not in moduleSetup._usedIOs.keys()
    assert value[1] in moduleSetup._openIOs

@pytest.mark.parametrize("value",testCases)
def testSetOutput(moduleSetup: GPIOControl, value: list):
    moduleSetup.newIO(value[2],value[0],value[1])
    if value[2] == IOType.OUTPUT:
        moduleSetup.setOutput(value[0])
        assert moduleSetup.getIOState(value[0])
    elif value[2] == IOType.INPUT:
        with pytest.raises(TypeError):
            moduleSetup.setOutputState(value[0])

@pytest.mark.parametrize("value",testCases)
def testSetOutput(functionSetup: GPIOControl, value: list):
    functionSetup.newIO(value[2],value[0],value[1])
    if value[2] == IOType.OUTPUT:
        functionSetup.setOutput(value[0])
        assert functionSetup.getIOState(value[0])
    elif value[2] == IOType.INPUT:
        with pytest.raises(TypeError):
            functionSetup.setOutput(value[0])


@pytest.mark.parametrize("value",testCases)
def testResetOutput(functionSetup: GPIOControl, value: list):
    functionSetup.newIO(value[2],value[0],value[1])
    if value[2] == IOType.OUTPUT:
        functionSetup.resetOutput(value[0])
        assert not functionSetup.getIOState(value[0])
    elif value[2] == IOType.INPUT:
        with pytest.raises(TypeError):
            functionSetup.resetOutput(value[0])