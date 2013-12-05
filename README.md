CurrentVoltage
==============

current voltage measurement with arduino

ReadAnalogPin.ino reads pin A0 on the Arduino and passes it to the serial port.

CurrentVoltage.py reads the serial port and stores the data (standart ttyUSB0).
After collecting the data for a given amount of time, it calculates the area under the curve and prints out the value in coulomb (ampere * seconds)

Usage: ~ $ python CurrentVoltage.py n m
n is the number of seconds to collect data.
m is the y size of the live plot
