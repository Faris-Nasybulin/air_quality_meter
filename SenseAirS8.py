import logging
import time

from pymodbus import ExceptionResponse, ModbusException
from pymodbus.client import ModbusSerialClient

#print(help(ModbusSerialClient))

#client = ModbusSerialClient('/dev/ttyAMA0', baudrate=9600)
#client.connect()
#result = client.read_input_registers(3, slave=254)

# result = client.read_input_registers(25, count=6, slave=254)

#result = client.read_input_registers(0, count=4, slave=254)
# result = client.read_holding_registers(31, slave=254)
# result = client.write_register(31,0, slave=254)
#result = client.read_input_registers(4, count=1, slave=254)
#print('result', result)
#client.close()

class SenseAirS8:
    CO2_INPUT_REGISTER_INDEX = 3
    ABC_PERIOD_HOLDING_REGISTER_INDEX = 31

    def __init__(self, tty='/dev/ttyAMA0', baudrate=9600, device_id=254):
        self.tty = tty
        self.baudrate = baudrate
        self.client = ModbusSerialClient(tty, baudrate=baudrate)
        self.device_id = device_id

    def check_response(self, response):
        if response.isError():
            if isinstance(response, ExceptionResponse):
                raise Exception(response)
            else:
                raise ModbusException(response)

    def readCO2(self):
        response = self.client.read_input_registers(self.CO2_INPUT_REGISTER_INDEX, device_id=self.device_id)

        self.check_response(response)

        return response.registers[0]

    def read_sys_info(self):
        response = self.client.read_input_registers(25, count=6, device_id=self.device_id)

        self.check_response(response)

        (typeIDHigh, typeIDLow, memoryMapVersion, FWVersionSummed, IDHigh, IDLow) = response.registers

        typeID = typeIDHigh * pow(2, 16) + typeIDLow
        FWMainVersion = FWVersionSummed // pow(2, 8)
        FWSubVersion = FWVersionSummed % pow(2, 8)
        FWVersion = str(FWMainVersion) + '.' + str(FWSubVersion)
        ID = IDHigh * pow(2, 16) + IDLow

        return {
            "typeID": typeID,
            "memoryMapVersion": memoryMapVersion,
            "FWVersion": FWVersion,
            "ID": ID,

            "FWMainVersion": FWMainVersion,
            "FWSubVersion": FWSubVersion,

            "typeIDHigh": typeIDHigh,
            "typeIDLow": typeIDLow,
            "FWVersionSummed": FWVersionSummed,
            "IDHigh": IDHigh,
            "IDLow": IDLow
        }

    def read_ABC_period(self):
        response = self.client.read_holding_registers(self.ABC_PERIOD_HOLDING_REGISTER_INDEX, device_id=self.device_id)

        self.check_response(response)

        return response.registers[0]

    @property
    def value(self):
        return self.readCO2()