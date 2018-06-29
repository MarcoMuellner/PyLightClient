import pytest
from hardware.GPIOControl import GPIOControl
from PyLightCommon.pylightcommon.models import EnumIOType

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture(scope='module')
def moduleSetup(request):
    return GPIOControl.inst()

@pytest.fixture(scope='function')
def functionSetup(request):
    return GPIOControl.inst()

testCases = [("One",3,EnumIOType.OUTPUT.value),
             ("Two",5,EnumIOType.OUTPUT.value),
             (3,7,EnumIOType.OUTPUT.value),
             (4.0,8,EnumIOType.OUTPUT.value),
             ("Five",3,EnumIOType.OUTPUT.value),
             ("Six", 10,EnumIOType.INPUT.value),
             ("Seven", 11,EnumIOType.INPUT.value),
             (8, 12,EnumIOType.INPUT.value),
             (9.0, 13,EnumIOType.INPUT.value),
             ("Ten", 10,EnumIOType.INPUT.value)
             ]

@pytest.mark.parametrize("value",testCases)
def testNewOutput(moduleSetup: GPIOControl, value: list):
    if value[2] == EnumIOType.OUTPUT:
        assert moduleSetup.newOutput(value[0],value[1])
        assert value[0] in moduleSetup._usedIOs.keys()
        assert value[1] not in moduleSetup._openIOs


@pytest.mark.parametrize("value",testCases)
def testNewInput(moduleSetup: GPIOControl, value: list):
    if value[2] == EnumIOType.INPUT:
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
    if value[2] == EnumIOType.OUTPUT:
        moduleSetup.setOutput(value[0])
        assert moduleSetup.getIOState(value[0])
    elif value[2] == EnumIOType.INPUT:
        with pytest.raises(TypeError):
            moduleSetup.setOutputState(value[0])

@pytest.mark.parametrize("value",testCases)
def testSetOutput(functionSetup: GPIOControl, value: list):
    functionSetup.newIO(value[2],value[0],value[1])
    if value[2] == EnumIOType.OUTPUT:
        functionSetup.setOutput(value[0])
        assert functionSetup.getIOState(value[0])
    elif value[2] == EnumIOType.INPUT:
        with pytest.raises(TypeError):
            functionSetup.setOutput(value[0])


@pytest.mark.parametrize("value",testCases)
def testResetOutput(functionSetup: GPIOControl, value: list):
    functionSetup.newIO(value[2],value[0],value[1])
    if value[2] == EnumIOType.OUTPUT:
        functionSetup.resetOutput(value[0])
        assert not functionSetup.getIOState(value[0])
    elif value[2] == EnumIOType.INPUT:
        with pytest.raises(TypeError):
            functionSetup.resetOutput(value[0])