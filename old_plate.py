from time import sleep
import machine


adc         = machine.ADC(machine.Pin(35))
adc_total   = machine.ADC(machine.Pin(34))
adc.atten(adc.ATTN_6DB)
adc_total.atten(adc.ATTN_11DB)
dac  = machine.DAC(machine.Pin(25))

mosfet = machine.Pin(16, machine.Pin.OUT)

tresh = 5.0
res_shunt = 10.0e3
res_prot = 10.0e3

res_tb = 100.0e3
res_ts = 10.0e3

def voltage_shunt():
    raw = adc.read()
    #print(adc.read())
    #voltage = (raw/2**12)*3.9
    return raw/1000

def total_current():
    return voltage_shunt()/res_shunt

def voltage_protection():
    return total_current()*res_prot

def voltage_sensor(total_voltage):
    return total_voltage-voltage_shunt()-voltage_protection()

def res_sensor(total_voltage):
    return voltage_sensor(total_voltage)/total_current()
    
def power_sensor(total_voltage):
    return voltage_sensor(total_voltage)*total_current()

def set_opamp_voltage(voltage):
    value = (voltage/(3.3/255))/10.0
    dac.write(int(value))

#int((d/255*3.3*10-adc.read()/1000)/(adc.read()/(1000*1e3))); sleep(0.1); dac.write(d)

mosfet.value(1)

while True:
    total_voltage = (adc_total.read()*(1+res_tb/res_ts))/1000.0
    #print("Voltage: {0:.1}, V[shunt]: {1:.2}, V[sens]: {2:.2}, R[k_sens]: {3:.3} P_mW[S]: {4:.4}                              ".format(total_voltage, voltage_shunt(), voltage_sensor(total_voltage), res_sensor(total_voltage)/1000.0, power_sensor(total_voltage)*1000 ),end="\r")
    print("Voltage: {0:.1}, V[shunt]: {1:.2}, V[sens]: {2:.2}, R[k_sens]: {3:.3} P_mW[S]: {4:.4}                              ".format(total_voltage, voltage_shunt(), voltage_sensor(total_voltage), res_sensor(total_voltage)/1000.0, power_sensor(total_voltage)*1000 ))
    #print(power_sensor(total_voltage)*1000)
    if ((power_sensor(total_voltage)*1000) > tresh):
        mosfet.value(0)
        #print("off")
        #res_shunt = 60.0e3
    #else:
    #    #print("on")
    #    res_shunt = 10.0e3
    #    mosfet.value(1)
    #sleep(0.1)

