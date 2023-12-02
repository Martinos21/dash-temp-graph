
from pymodbus.client import ModbusSerialClient as ModbusClient


#digital_inputs = 817

client = ModbusClient(method='rtu', port='COM4',
                       baudrate=19200, parity="N", stopbits=1,  timeout=2)

client.connect()


#read = client.write_coil(address=0x330, value=False, slave=1)
#read = client.read_holding_registers(address=4, count=1, slave=1)
read = client.read_input_registers(address=3302, count=1, slave=1)
#read = client.read_discrete_inputs(address=3302, count=1, slave=1)

print(read.registers)


"""counter_err = 0
counter_read = 0"""
"""""
client = ModbusSerial("/dev/tty.usbserial-0001")

# connect to device
client.connect()

# set/set information
rr = client.read_coils(817)
write = client.write_coil(817, value=True, slave=1)
print(write)
# disconnect device
client.close()
"""""
"""""
port = "/dev/tty.usbserial-0001"
timeout = 1
baudrate = 19200
parity = "N"
stopbits = 1
bytesize = 8
slave_unit = 3
"""""


"""""
def read_coi(register):
    result = client.read_input_registers(register, 2, unit=slave_unit)
    print(result)    


client = ModbusSerialClient(method='rtu', port=port, timeout=timeout,
                                   baudrate=baudrate, parity=parity,
                                   stopbits=stopbits,bytesize=bytesize)

client.connect()
# print(conn_status)
write = client.write_coils(digital_inputs, values=1, slave=slave_unit)
# rt = client.regi(0x330, 1, slave_unit)
# data = read.registers[int(1)]
print(write)

# read_input(digital_inputs)
client.close()
"""


