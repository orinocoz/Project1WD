from RPi import GPIO
import spidev
import MySQLdb
import time

class MCP3008:
    def __init__(self, bus=0, device=0):
        self.__bus = bus
        self.__device = device

        @property
        def bus(self):
            return self.__bus

        @bus.setter
        def bus(self, value):
            try:
                self.__bus  = int(value)
            except ValueError:
                print("fout")

        @property
        def device(self):
            return self.__device

        @device.setter
        def device(self, value):
            try:
                self.__device = int(value)
            except ValueError:
                print("fout")


    def read_channel(self, ch):
        spi = spidev.SpiDev()
        spi.open(self.__bus, self.__device)
        spi.max_speed_hz = 5000

        bytes_out = [0x1, self.shift_bits(ch), 0x00]
        bytes_in = spi.xfer2(bytes_out)

        woord = bytes_in[1] << 8
        woord = woord | bytes_in[2]
        return woord

    def shift_bits(self, ch):
        tot = (ch <<4) | 0x80

        return tot

    def rain(self):
        value = self.read_channel(int(0))
        if value > 400:
            res = 3 #veel regen
        elif value > 150:
            res = 2 #beetje regen
        else:
            res = 1 #geen regen
        return res

    def wind_speed(self):
        value = self.read_channel(int(1))
        volt = (value / 1023.0) * 3.3
        if volt <= 0.4:
            wind_speed = 0
        else:
            wind_speed = (volt - 0.4) * 32.4
        return wind_speed


MCP = MCP3008()
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
    insert_into_db(6, MCP.rain())
    insert_into_db(7, MCP.wind_speed())
    db.close()
    GPIO.setwarnings(False)  # get rid of warning when no GPIO pins set up
    GPIO.cleanup()

if __name__ == '__main__':
    main()