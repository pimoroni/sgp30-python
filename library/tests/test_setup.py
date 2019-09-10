_test_data = {
    'init_air_quality': [0x03, 0x20],
    'measure_air_quality': [0x08, 0x20],
    'get_baseline': [0x15, 0x20],
    'set_baseline': [0x1e, 0x20, 0xFE, 0xCA, 0x68, 0xFE, 0xCA, 0x68],
    'set_humidity': [0x61, 0x20, 0xFE, 0xCA, 0x68],
    'measure_test': [0x32, 0x20],
    'get_feature_set_version': [0x2f, 0x20],
    'measure_raw_signals': [0x50, 0x20],
    'get_serial_id': [0x82, 0x36]
}


def test_commands():
    import sgp30
    sgp30 = sgp30.SGP30()

    for command_name in sgp30.commands.keys():
        cmd, param_len, response_len = sgp30.commands[command_name]
        args = [0xCAFE] * param_len
        result = sgp30.command(command_name, args)
        assert _test_data[command_name] == [ord(n) for n in result]
