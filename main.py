import ads1x15
import hp4067
import machine
import math
from time import sleep

ads_address = 72
gain = 0
rate = 6

R_mux = [
        1000e3,
        470e3,
        220e3,
        100e3,
        10e3,
        4.7e3
        ]

pin_en = machine.Pin(25, machine.Pin.OUT)
pin_s0 = machine.Pin(19, machine.Pin.OUT)
pin_s1 = machine.Pin(18, machine.Pin.OUT)
pin_s2 = machine.Pin(5,  machine.Pin.OUT)
pin_s3 = machine.Pin(17, machine.Pin.OUT)

muxer = hp4067.HP4067(pin_en, pin_s0, pin_s1, pin_s2, pin_s3)
muxer.enable()
muxer.set_channel(0)

pin_scl = machine.Pin(22)
pin_sda = machine.Pin(23)
i2c = machine.I2C(sda = pin_sda, scl = pin_scl, freq=400000)

adc = ads1x15.ADS1015(i2c, ads_address, gain)

while True:
    for ch in range(0, 4):
        muxer.set_channel(ch)
        v_log  = adc.raw_to_v(adc.read(rate,0))
        v_real = adc.raw_to_v(adc.read(rate,1))
        print("MUX_ch: {0}, V_log: {1}, V_real: {2}".format(ch, v_log, v_real))
        sleep(3)
