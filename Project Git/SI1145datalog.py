import smbus
import time
import MySQLdb
from RPi import GPIO


REG_IR = 0x04
REG_INTCFG = 0x03
REG_COMMAND = 0x18
class SI1145:
    def __init__(self, address,i2cbus=1):
        self.__bus = smbus.SMBus(i2cbus)
        self.__address = address
        self.__reset()
        self.__calibrate()

    def __read(self, register):
        res = self.__bus.read_byte_data(self.__address, register) & 0xFFFF
        return res


    def __write(self, register, value):
            value = value & 0xFF
            self.__bus.write_byte_data(self.__address, register, value)

    def __write_param(self, p1, p2):
        self.__write(0x17, p2)
        self.__write(REG_COMMAND, p1 | 0xA0)
        parameter_value = self.__read(0x2E)
        return parameter_value

    def __reset(self):
        self.__write(0x08,0)
        self.__write(0x09, 0)
        self.__write(REG_IR, 0)
        self.__write(0x05, 0)
        self.__write(0x06, 0)
        self.__write(REG_INTCFG, 0)
        self.__write(0x21, 0xFF)
        self.__write(REG_COMMAND, 0x01)
        time.sleep(0.01)
        self.__write(0x07,0x17)
        time.sleep(0.01)

    def __calibrate(self):
        self.__write(0x13, 0x29)
        self.__write(0x14, 0x89)
        self.__write(0x15, 0x02)
        self.__write(0x16, 0x00)
        self.__write_param(0x01, 0x80 | 0x20 | 0x10 | 0x01)
        self.__write(REG_INTCFG, 0x01)
        self.__write(REG_IR, 0x01)

        self.__write_param(0x0E, 0x00)
        self.__write_param(0x1E, 0)
        self.__write_param(0x1D, 0x70)
        self.__write_param(0x1F, 0x20)
        self.__write_param(0x11, 0)
        self.__write_param(0x10, 0x70)
        self.__write_param(0x12, 0x20)
        self.__write(0x08, 0xFF)
        self.__write(REG_COMMAND, 0x0F)

    def readUV(self):
        return self.__read(0x2C)

    def readVisible(self):
        return self.__read(0x22)

sii1145 = SI1145(0x60)
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
    time.sleep(5)
    GPIO.setmode(GPIO.BCM)
    insert_into_db(4, sii1145.readUV())
    insert_into_db(5, sii1145.readVisible())
    db.close()
    GPIO.setwarnings(False)  # get rid of warning when no GPIO pins set up
    GPIO.cleanup()

if __name__ == '__main__':
    main()




















