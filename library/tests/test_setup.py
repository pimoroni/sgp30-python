from tools import MockI2CDev, MockI2CMsg


def test_setup():
    from sgp30 import SGP30
    sgp30 = SGP30(i2c_dev=MockI2CDev(), i2c_msg=MockI2CMsg())
    del sgp30


def test_get_unique_id():
    from sgp30 import SGP30
    sgp30 = SGP30(i2c_dev=MockI2CDev(), i2c_msg=MockI2CMsg())
    assert sgp30.get_unique_id() == 0xffffffffffff


def test_get_feature_set_version():
    from sgp30 import SGP30
    sgp30 = SGP30(i2c_dev=MockI2CDev(), i2c_msg=MockI2CMsg())
    assert sgp30.get_feature_set_version() == (0xc, 0xfe)
