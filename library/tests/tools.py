import struct


class MockI2CDev():
    def __init__(self):
        self._last_write = None

    def i2c_rdwr(self, a, b=None):
        if isinstance(a, MockI2CMsgW):
            self._last_write = a.process()
        if isinstance(a, MockI2CMsgR):
            a.process(self._last_write)
        if b is not None:
            b.process(self._last_write)


class MockI2CMsg():
    def write(self, i2c_addr, data):
        return MockI2CMsgW(i2c_addr, data)

    def read(self, i2c_addr, response_len):
        return MockI2CMsgR(i2c_addr, response_len)


class MockI2CMsgR():
    def __init__(self, i2c_addr, response_len):
        self._num_words = response_len // 3
        self.buf = None

    def process(self, last_command):
        result = [0, 0, 0]
        if last_command[0] == 0x3682:  # get_serial_id
            result = [0xffff, 0xffff, 0xffff]
        if last_command[0] == 0x202f:  # get_feature_set_version
            result = [0xCAFE, 0x0000, 0x0000]

        buf = []

        for i in range(self._num_words):
            word = result[i]
            packed = bytearray(struct.pack('>H', word))
            buf.append(packed[0])
            buf.append(packed[1])
            buf.append(self.calculate_crc(word))

        self.buf = bytearray(buf)


    def calculate_crc(self, data):
        """Calculate an 8-bit CRC from a 16-bit word

        Defined in section 6.6 of the SGP30 datasheet.

        Polynominal: 0x31 (x8 + x5 + x4 + x1)
        Initialization: 0xFF
        Reflect input/output: False
        Final XOR: 0x00

        """
        crc = 0xff  # Initialization value
        # calculates 8-Bit checksum with given polynomial
        for byte in [(data & 0xff00) >> 8, data & 0x00ff]:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31  # XOR with polynominal
                else:
                    crc <<= 1
        return crc & 0xff


class MockI2CMsgW():
    def __init__(self, i2c_addr, data):
        self._data = data

    def process(self):
        command_len = (len(self._data) - 2) // 3
        return struct.unpack('>H' + ('Hx' * command_len), self._data)
