import smbus
import time
import MySQLdb
import math
from RPi import GPIO

SLEEP = 0
FORCED = 1
RESETADDR = 0xe0
RESETWRITE = 0xb6
TP_MODE_ADDRESS = 0x74
MODE_MSK = 0x03
MODE_POS = 0
CALCO_ADDR1 = 0x89
CALCO_ADDR2 = 0xe1
CALCO_ADDR1_LEN = 25
CALCO_ADDR2_LEN = 16
OS_NONE = 0
OS1 = 1
OS2 = 2
OS4 = 3
OS8 = 4
OS16 = 5
OSHUMIDITY_ADDR = 0x72
OSHUMIDITY_MSK = 0X07
OSHUMIDITY_POS = 0
OSPRESSURE_MSK = 0X1C
OSPRESSURE_POS = 2
OSTEMPERATURE_MSK = 0XE0
OSTEMPERATURE_POS = 5
FILTER_ADDR = 0x75
FILTER_MSK = 0X1C
FILTER_POS = 2
MEASUREMENT_ADDR = 0x1d
MEASUREMENT_LENGTH = 15

class BME680:
    def __init__(self, address,i2cbus=1):
        self.__bus = smbus.SMBus(i2cbus)
        self.__address = address
        self.offset_temp_in_t_fine = None
        self.os_hum = None
        self.os_temp = None
        self.os_pres = None
        self.filter = None
        self.power_mode = None
        self.calibration_data = CalibrationData()
        self.calibrate()
        self.data = FieldData()


        self.reset()
        self.set_mode(SLEEP)
        self.set_humidity_oversample(OS2)
        self.set_temperature_oversample(OS8)
        self.set_pressure_oversample(OS4)
        self.set_filter(2)
        self.set_temp_offset(0)
        self.get_data()



    def set_bits(self, register, mask, position, value):
        temp = self.__read(register, 1)
        temp &= ~mask
        temp |= value << position
        self.__write(register, temp)

    def __read(self, register, length):
        if length ==1:
            return self.__bus.read_byte_data(self.__address, register)
        else:
            return self.__bus.read_i2c_block_data(self.__address, register, length)

    def __write(self, register, value):
        if isinstance(value, int):
            self.__bus.write_byte_data(self.__address, register, value)
        else:
            self.__bus.write_i2c_block_data(self.__address, register, value)

    def reset(self):
        self.__write(RESETADDR,RESETWRITE)

    def set_mode(self, mode):
        self.power_mode = mode
        self.set_bits(TP_MODE_ADDRESS, MODE_MSK, MODE_POS, mode)

    def get_mode(self):
        self.power_mode = self.__read(TP_MODE_ADDRESS, 1)
        return self.power_mode

    def set_temp_offset(self, value):
        if value == 0:
            self.offset_temp_in_t_fine = 0
        else:
            self.offset_temp_in_t_fine = int(math.copysign((((int(abs(value) * 100)) << 8) - 128) / 5, value))

    def calibrate(self):
        calibration = self.__read(CALCO_ADDR1, CALCO_ADDR1_LEN)
        calibration += self.__read(CALCO_ADDR2, CALCO_ADDR2_LEN)
        self.calibration_data.set_from_array(calibration)


    #OVERSAMPLES SET + GET
    #
    #
    #
    def set_humidity_oversample(self, value):
        self.os_hum = value
        self.set_bits(OSHUMIDITY_ADDR, OSHUMIDITY_MSK, OSHUMIDITY_POS, value)

    def get_humidity_oversample(self):
        return (self.__read(OSHUMIDITY_ADDR, 1) & OSHUMIDITY_MSK) >> OSHUMIDITY_POS

    def set_pressure_oversample(self, value):
        self.os_pres = value
        self.set_bits(TP_MODE_ADDRESS, OSPRESSURE_MSK, OSPRESSURE_POS, value)

    def get_pressure_oversample(self):
        return (self.__read(TP_MODE_ADDRESS, 1) & OSPRESSURE_MSK) >> OSPRESSURE_POS

    def set_temperature_oversample(self, value):
        self.os_temp = value
        self.set_bits(TP_MODE_ADDRESS, OSTEMPERATURE_MSK, OSTEMPERATURE_POS, value)

    def get_temperature_oversample(self):
        return (self.__read(TP_MODE_ADDRESS, 1) & OSTEMPERATURE_MSK) >> OSTEMPERATURE_POS

    def set_filter(self, value):
        self.filter = value
        self.set_bits(FILTER_ADDR, FILTER_MSK, FILTER_POS, value)

    def get_filter(self):
        return (self.__read(FILTER_ADDR, 1) & FILTER_MSK) >> FILTER_POS

    #GETTING DATA + CALCULATION
    #
    #
    #
    def get_data(self):
        self.set_mode(FORCED)
        for attempt in range(10):
            time.sleep(0.10)
            regs = self.__read(MEASUREMENT_ADDR, MEASUREMENT_LENGTH)
            adc_pres = (regs[2] << 12) | (regs[3] << 4) | (regs[4] >> 4)
            adc_temp = (regs[5] << 12) | (regs[6] << 4) | (regs[7] >> 4)
            adc_hum = (regs[8] << 8) | regs[9]

            self.data.temperature = self.calc_temperature(adc_temp) /100.0
            self.data.pressure = self.calc_pressure(adc_pres) / 100.0
            self.data.humidity = self.calc_humidity(adc_hum) / 1000.0
            return True

        return False

    def calc_temperature(self, temperature_adc):
        var1 = (temperature_adc >> 3) - (self.calibration_data.t1 << 1)
        var2 = (var1 * self.calibration_data.t2) >> 11
        var3 = ((var1 >> 1) * (var1 >> 1)) >> 12
        var3 = (var3 * (self.calibration_data.t3 << 4)) >> 14

        # Save temperature data for pressure calculations
        self.calibration_data.t_fine = (var2 + var3) + self.offset_temp_in_t_fine
        calc_temp = (((self.calibration_data.t_fine * 5) + 128) >> 8)

        return calc_temp

    def calc_pressure(self, pressure_adc):
        var1 = (self.calibration_data.t_fine >> 1) - 64000
        var2 = ((((var1 >> 2) * (var1 >> 2)) >> 11) *
                self.calibration_data.p6) >> 2
        var2 = var2 + ((var1 * self.calibration_data.p5) << 1)
        var2 = (var2 >> 2) + (self.calibration_data.p4 << 16)
        var1 = (((((var1 >> 2) * (var1 >> 2)) >> 13) *
                 (self.calibration_data.p3 << 5) >> 3) +
                ((self.calibration_data.p2 * var1) >> 1))
        var1 = var1 >> 18

        var1 = ((32768 + var1) * self.calibration_data.p1) >> 15
        calc_pressure = 1048576 - pressure_adc
        calc_pressure = ((calc_pressure - (var2 >> 12)) * 3125)

        if calc_pressure >= (1 << 31):
            calc_pressure = ((calc_pressure // var1) << 1)
        else:
            calc_pressure = ((calc_pressure << 1) // var1)

        var1 = (self.calibration_data.p9 * (((calc_pressure >> 3) *
                                                 (calc_pressure >> 3)) >> 13)) >> 12
        var2 = ((calc_pressure >> 2) *
                self.calibration_data.p8) >> 13
        var3 = ((calc_pressure >> 8) * (calc_pressure >> 8) *
                (calc_pressure >> 8) *
                self.calibration_data.p10) >> 17

        calc_pressure = calc_pressure + ((var1 + var2 + var3 +
                                            (self.calibration_data.p7 << 7)) >> 4)

        return calc_pressure

    def calc_humidity(self, humidity_adc):
        temp_scaled = ((self.calibration_data.t_fine * 5) + 128) >> 8
        var1 = (humidity_adc - (self.calibration_data.h1 * 16)) \
               - (((temp_scaled * self.calibration_data.h3) // 100) >> 1)
        var2 = (self.calibration_data.h2
                * (((temp_scaled * self.calibration_data.h4) // 100)
                   + (((temp_scaled * ((temp_scaled * self.calibration_data.h5) // 100)) >> 6)
                      // 100) + (1 * 16384))) >> 10
        var3 = var1 * var2
        var4 = self.calibration_data.h6 << 7
        var4 = (var4 + ((temp_scaled * self.calibration_data.h7) // 100)) >> 4
        var5 = ((var3 >> 14) * (var3 >> 14)) >> 10
        var6 = (var4 * var5) >> 1
        calc_hum = (((var3 + var6) >> 10) * 1000) >> 12

        return min(max(calc_hum, 0), 100000)


T2_LSB_REG = 1
T2_MSB_REG = 2
T3_REG = 3
P1_LSB_REG = 5
P1_MSB_REG = 6
P2_LSB_REG = 7
P2_MSB_REG = 8
P3_REG = 9
P4_LSB_REG = 11
P4_MSB_REG = 12
P5_LSB_REG = 13
P5_MSB_REG = 14
P7_REG = 15
P6_REG = 16
P8_LSB_REG = 19
P8_MSB_REG = 20
P9_LSB_REG = 21
P9_MSB_REG = 22
P10_REG = 23
H2_MSB_REG = 25
H2_LSB_REG = 26
H1_LSB_REG = 26
H1_MSB_REG = 27
H3_REG = 28
H4_REG = 29
H5_REG = 30
H6_REG = 31
H7_REG = 32
T1_LSB_REG = 33
T1_MSB_REG = 34

COMP_HUMIDITY = 4
BIT_H1_DATA_MSK = 0x0F
class CalibrationData:
    def __init__(self):
        self.h1 = None
        self.h2 = None
        self.h3 = None
        self.h4 = None
        self.h5 = None
        self.h6 = None
        self.h7 = None
        self.t1 = None
        self.t2 = None
        self.t3 = None
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None
        self.p5 = None
        self.p6 = None
        self.p7 = None
        self.p8 = None
        self.p9 = None
        self.p10 = None
        self.t_fine = None

    def set_from_array(self, calibration):
        # Temperature COF
        self.t1 = bytes_to_words(calibration[T1_MSB_REG], calibration[T1_LSB_REG])
        self.t2 = bytes_to_words(calibration[T2_MSB_REG], calibration[T2_LSB_REG], bits=16, signed=True)
        self.t3 = two_comp(calibration[T3_REG], bits=8)

        # Pressure COF
        self.p1 = bytes_to_words(calibration[P1_MSB_REG], calibration[P1_LSB_REG])
        self.p2 = bytes_to_words(calibration[P2_MSB_REG], calibration[P2_LSB_REG], bits=16, signed=True)
        self.p3 = two_comp(calibration[P3_REG], bits=8)
        self.p4 = bytes_to_words(calibration[P4_MSB_REG], calibration[P4_LSB_REG], bits=16, signed=True)
        self.p5 = bytes_to_words(calibration[P5_MSB_REG], calibration[P5_LSB_REG], bits=16, signed=True)
        self.p6 = two_comp(calibration[P6_REG], bits=8)
        self.p7 = two_comp(calibration[P7_REG], bits=8)
        self.p8 = bytes_to_words(calibration[P8_MSB_REG], calibration[P8_LSB_REG], bits=16, signed=True)
        self.p9 = bytes_to_words(calibration[P9_MSB_REG], calibration[P9_LSB_REG], bits=16, signed=True)
        self.p10 = calibration[P10_REG]

        # Humidity related coefficients
        self.h1 = (calibration[H1_MSB_REG] << COMP_HUMIDITY) | (calibration[H1_LSB_REG] & BIT_H1_DATA_MSK)
        self.h2 = (calibration[H2_MSB_REG] << COMP_HUMIDITY) | (calibration[H2_LSB_REG] >> COMP_HUMIDITY)
        self.h3 = two_comp(calibration[H3_REG], bits=8)
        self.h4 = two_comp(calibration[H4_REG], bits=8)
        self.h5 = two_comp(calibration[H5_REG], bits=8)
        self.h6 = calibration[H6_REG]
        self.h7 = two_comp(calibration[H7_REG], bits=8)

def bytes_to_words(msb, lsb, bits=16, signed=False):
    word = (msb << 8) | lsb
    if signed:
        word = two_comp(word, bits)
    return word

def two_comp(val, bits=16):
    if val & (1 << (bits - 1)) != 0:
        val = val - (1 << bits)
    return val

class FieldData:
    def __init__(self):
        # Temperature in degree celsius x100
        self.temperature = None
        # Pressure in Pascal
        self.pressure = None
        # Humidity in % relative humidity x1000
        self.humidity = None

bme680 = BME680(0x77)
db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="lex5690",
                         db="weatherstationdeluxe")

def insert_into_db(sensor, data):
    cursor = db.cursor()
    sql = '''INSERT INTO history(sensorID,value) VALUES ({0},{1})'''.format(sensor,data)
    cursor.execute(sql)
    db.commit()

def main():
    GPIO.setmode(GPIO.BCM)
    bme680.get_data()
    insert_into_db(1, bme680.data.temperature)
    insert_into_db(2, bme680.data.pressure)
    insert_into_db(3, bme680.data.humidity)
    db.close()
    GPIO.setwarnings(False)  # get rid of warning when no GPIO pins set up
    GPIO.cleanup()

if __name__ == '__main__':
    main()
