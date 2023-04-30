import pykson

class Class1(pykson.JsonObject):
    variable_1 = pykson.IntegerField(default_value=1)

class Class2(Class1):
    variable_2 = pykson.IntegerField(default_value=2)

class Class3(Class2):
    variable_3 = pykson.IntegerField(default_value=3)

class Class4(Class3):
    variable_4 = pykson.IntegerField(default_value=4)

def test_multiple_inheritance():
    class4 = Class4()
    assert class4.variable_1 == 1
    assert class4.variable_2 == 2
    assert class4.variable_3 == 3
    assert class4.variable_4 == 4