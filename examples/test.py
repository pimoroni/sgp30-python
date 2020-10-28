from sgp30 import SGP30
import time
import sys

sgp30 = SGP30()

# result = sgp30.command('set_baseline', (0xFECA, 0xBEBA))
# result = sgp30.command('get_baseline')
# print(["{:02x}".format(n) for n in result])

print("Sensor warming up, please wait...")
def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

sgp30.start_measurement(crude_progress_bar)
sys.stdout.write('\n')

while True:
    result = sgp30.get_air_quality()
    print(result)
    time.sleep(1.0)
