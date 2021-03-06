import ads1x15
import hp4067
import machine
import math
import json
import sys
from time import sleep

# DAC Setup
dac  = machine.DAC(machine.Pin(25))

# Multiplexer Setup
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

# ADC Setup
ads_address = 72
adc_gain = 0
adc_rate = 6

pin_scl = machine.Pin(22)
pin_sda = machine.Pin(23)
i2c = machine.I2C(sda = pin_sda, scl = pin_scl, freq=400000)
adc = ads1x15.ADS1015(i2c, ads_address, adc_gain)

# Functions
def voltage_shunt():
    return adc.raw_to_v(adc.read(get_adc_rate(), 0))

def total_current(v_shunt):
    return v_shunt/R_mux[muxer.get_channel()]

def voltage_sensor(v_shunt):
    total_voltage = get_total_voltage()
    return total_voltage-v_shunt

def res_sensor(v_shunt):
    return voltage_sensor(v_shunt)/total_current(v_shunt)
    
def power_sensor(v_shunt):
    total_voltage = get_total_voltage()
    return voltage_sensor(v_shunt)*total_current(v_shunt)

def set_total_voltage(voltage):
    global total_voltage
    total_voltage = voltage
    value = ((total_voltage)/(3.3/255))/11.0
    dac.write(int(value))

def get_total_voltage():
    return total_voltage

def set_adc_gain(gain):
    global adc_gain
    global adc
    adc_gain = gain
    adc.gain = gain

def get_adc_gain():
    return adc_gain

def set_adc_rate(rate):
    global adc_rate
    adc_rate = rate
def get_adc_rate():
    return adc_rate


def set_settings(set_dict):
    global total_voltage
    global adc_gain
    global adc_rate
    setters = {
                'v_tot': set_total_voltage, 
                'adc_gain' : set_adc_gain,
                'adc_rate' : set_adc_rate,
                'mux_chan': muxer.set_channel,
                }
    for key in setters.keys():
        if key in set_dict.keys():
            setters[key](set_dict[key])


set_total_voltage(10)

v_lower = 1
v_upper = 4.5

# max voltage of psu - opamp offset
total_max = 19

p_lower = 0
p_upper = 5

p_sens_last = 0

data_dict = {}

while True:
    #v_shunt = voltage_shunt()
    #r_sensor = res_sensor(total_voltage, v_shunt)/1000.0
    #p_sensor = power_sensor(total_voltage, v_shunt)*1000.0

    rec_raw = sys.stdin.readline()
    try:
        set_dict = json.loads(rec_raw.strip())
    except:
        set_dict = {}

    set_settings(set_dict)

    v_shunt = voltage_shunt()

    data_dict['v_shunt']  = v_shunt 
    data_dict['v_tot']    = get_total_voltage()
    data_dict['p_sens']   = power_sensor(v_shunt)
    data_dict['r_sens']   = res_sensor(v_shunt)
    data_dict['adc_gain'] = get_adc_gain()
    data_dict['adc_rate'] = get_adc_rate()
    data_dict['mux_chan'] = muxer.get_channel()
    data_dict['R_shunt']  = R_mux[muxer.get_channel()]

    print(json.dumps(data_dict))

    #if v_shunt < v_lower:
    #    if 0 == muxer.get_channel():
    #        print("muxer getting out of range (lower bound)")
    #    else:
    #        muxer.set_channel(muxer.get_channel()-1)
    #        continue
    #if v_shunt > v_upper:
    #    if len(R_mux) == muxer.get_channel():
    #        print("muxer getting out of range (upper bound)")
    #    else:
    #        muxer.set_channel(muxer.get_channel()+1)
    #        continue
    #if p_sensor < p_lower:
    #    # estimate drop rate
    #    # adjust accordingly
    #    if total_voltage+1 >= total_max:
    #        print("voltage getting out of range (upper bound)")
    #    else:
    #        total_voltage += 1
    #        set_opamp_voltage(total_voltage)
    #        continue
    #if p_sensor > p_upper:
    #    # estimate rise rate
    #    # adjust accordingly
    #    if total_voltage-1 <= 0:
    #        print("voltage getting out of range (upper bound)")
    #    else:
    #        total_voltage -= 1
    #        set_opamp_voltage(total_voltage)
    #        continue

    #p_rate = 0 if abs(p_sens_last-p_sensor) < 0.01 else p_sens_last-p_sensor
    #print("Total Voltage: {0:.3}, V[shunt]: {1:.3}".format(total_voltage, v_shunt))
    #print("R[k_sens]: {0:.4} P_mW[S]: {1:.4}".format(r_sensor, p_sensor))
    #print("R_shunt[k]: {0:.4} p_rate: {1:.4}".format(R_mux[muxer.get_channel()], p_rate))
    #p_sens_last = p_sensor
    sleep(0.5)

