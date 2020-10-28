# SGP30 Gas Sensor

[![Build Status](https://travis-ci.com/pimoroni/sgp30-python.svg?branch=master)](https://travis-ci.com/pimoroni/sgp30-python)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/sgp30-python/badge.svg?branch=master)](https://coveralls.io/github/pimoroni/sgp30-python?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/pimoroni-sgp30.svg)](https://pypi.python.org/pypi/pimoroni-sgp30)
[![Python Versions](https://img.shields.io/pypi/pyversions/pimoroni-sgp30.svg)](https://pypi.python.org/pypi/pimoroni-sgp30)

# Installing

Stable library from PyPi:

* Just run `sudo pip install pimoroni-sgp30`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/sgp30-python`
* `cd sgp30-python`
* `sudo ./install.sh`


# Changelog
0.0.2
-----

* BugFix: avoid infinite loop during start_measurement (thanks @millerdq2038)
* BugFix: corrected parameter order for set_baseline (thanks @phooey)
* Improvement: close i2c file handle to avoid leak (https://github.com/pimoroni/sgp30-python/issues/5)

0.0.1
-----

* Initial Release
