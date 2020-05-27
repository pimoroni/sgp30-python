import struct
import time


__version__ = '0.0.1'

SGP30_I2C_ADDR = 0x58


class SGP30Reading:
    __slots__ = 'equivalent_co2', 'total_voc'

    def __init__(self, eco2, tvoc):
        self.equivalent_co2 = eco2
        self.total_voc = tvoc

    def __str__(self):
        return """Air Quality:
Equivalent C02: {: 5d} (ppm)
Total VOC:      {: 5d} (ppb)
""".format(self.equivalent_co2, self.total_voc)


class SGP30:
    def __init__(self, i2c_dev=None, i2c_msg=None, i2c_addr=SGP30_I2C_ADDR):
        """Mapping table of SGP30 commands.

        Friendly-name, followed by 16-bit command,
        then the number of parameter and response words.

        Each word is two bytes followed by a third CRC
        checksum byte. So a response length of 2 would
        result in the transmission of 6 bytes total.
        """
        self.commands = {
            'init_air_quality': (0x2003, 0, 0),
            'measure_air_quality': (0x2008, 0, 2),
            'get_baseline': (0x2015, 0, 2),
            'set_baseline': (0x201e, 2, 0),
            'set_humidity': (0x2061, 1, 0),
            # 'measure_test': (0x2032, 0, 1),  # Production verification only
            'get_feature_set_version': (0x202f, 0, 1),
            'measure_raw_signals': (0x2050, 0, 2),
            'get_serial_id': (0x3682, 0, 3)
        }

        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._i2c_msg = i2c_msg
        if self._i2c_dev is None:
            from smbus2 import SMBus, i2c_msg
            self._i2c_msg = i2c_msg
            self._i2c_dev = SMBus(1)

    def command(self, command_name, parameters=None):
        if parameters is None:
            parameters = []
        parameters = list(parameters)
        cmd, param_len, response_len = self.commands[command_name]
        if len(parameters) != param_len:
            raise ValueError("{} requires {} parameters. {} supplied!".format(
                command_name,
                param_len,
                len(parameters)
            ))

        parameters_out = [cmd]

        for i in range(len(parameters)):
            parameters_out.append(parameters[i])
            parameters_out.append(self.calculate_crc(parameters[i]))

        data_out = struct.pack('>H' + ('HB' * param_len), *parameters_out)

        msg_w = self._i2c_msg.write(self._i2c_addr, data_out)
        self._i2c_dev.i2c_rdwr(msg_w)
        time.sleep(0.025)  # Suitable for all commands except 'measure_test'

        if response_len > 0:
            # Each parameter is a word (2 bytes) followed by a CRC (1 byte)
            msg_r = self._i2c_msg.read(self._i2c_addr, response_len * 3)
            self._i2c_dev.i2c_rdwr(msg_r)

            buf = msg_r.buf[0:response_len * 3]

            response = struct.unpack(
                '>' + ('HB' * response_len),
                buf)

            verified = []
            for i in range(response_len):
                offset = i * 2
                value, crc = response[offset:offset + 2]
                if crc != self.calculate_crc(value):
                    raise RuntimeError("Invalid CRC in response from SGP30: {:02x} != {:02x}",
                                       crc,
                                       self.calculate_crc(value),
                                       buf)
                verified.append(value)
            return verified

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

    def get_unique_id(self):
        result = self.command('get_serial_id')
        return result[0] << 32 | result[1] << 16 | result[0]

    def get_feature_set_version(self):
        result = self.command('get_feature_set_version')[0]
        return (result & 0xf000) >> 12, result & 0x00ff

    def start_measurement(self, run_while_waiting=None):
        """Start air quality measurement on the SGP30.

        The first 15 readings are discarded so this command will block for 15s.

        :param run_while_waiting: Function to call for every discarded reading.

        """
        self.command('init_air_quality')
        testsamples = 0
        while True:
            # Discard the initialisation readings as per page 8/15 of the datasheet
            eco2, tvoc = self.command('measure_air_quality')
            # The first 15 readings should return as 400, 0 so abort when they change
            # Break after 20 test samples to avoid a potential infinite loop
            if eco2 != 400 or tvoc != 0 or testsamples >= 20:
                break
            if callable(run_while_waiting):
                run_while_waiting()
            time.sleep(1.0)
            testsamples += 1

    def get_air_quality(self):
        """Get an air quality measurement.

        Returns an instance of SGP30Reading with the properties equivalent_co2 and total_voc.

        This should be called at 1s intervals to ensure the dynamic baseline compensation on the SGP30 operates correctly.

        """
        eco2, tvoc = self.command('measure_air_quality')
        return SGP30Reading(eco2, tvoc)

    def get_baseline(self):
        """Get the current baseline setting.

        Returns an instance of SGP30Reading with the properties equivalent_co2 and total_voc.

        """
        eco2, tvoc = self.command('get_baseline')
        return SGP30Reading(eco2, tvoc)

    def set_baseline(self, eco2, tvoc):
        self.command('set_baseline', eco2, tvoc)
