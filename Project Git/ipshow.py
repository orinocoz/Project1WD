import RPi.GPIO as GPIO
import time
import socket
import fcntl
import struct
import MySQLdb

# Define GPIO to LCD mapping
LCD_RS = 26
LCD_E = 19
LCD_D4 = 13
LCD_D5 = 6
LCD_D6 = 5
LCD_D7 = 20

condition = True

class LCD():
    def __init__(self,RS_Pin, E_Pin, D4_Pin, D5_Pin, D6_Pin, D7_Pin, LCD_WIDTH = 16):
        self.__RS = RS_Pin
        self.__E = E_Pin
        self.__D4 = D4_Pin
        self.__D5 = D5_Pin
        self.__D6 = D6_Pin
        self.__D7 = D7_Pin
        self.__LCD_WIDTH = LCD_WIDTH
        self.lcd_init()

    @property
    def RSpin(self):
        return self.__RS

    @property
    def Epin(self):
        return self.__E

    @property
    def D4pin(self):
        return self.__D4

    @property
    def D5pin(self):
        return self.__D5

    @property
    def D6pin(self):
        return self.__D6

    @property
    def D7pin(self):
        return self.__D7

    def lcd_init(self):
        # Initialise display
        self.lcd_byte(0x33, False)  # 110011 Initialise
        self.lcd_byte(0x32, False)  # 110010 Initialise
        self.lcd_byte(0x06, False)  # 000110 Cursor move direction
        self.lcd_byte(0x0C, False)  # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28, False)  # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, False)  # 000001 Clear display
        time.sleep(0.0005)

    def write_text(self, Line1, Line2):
            self.lcd_string(Line1, 0x80)  # LCD RAM address for the 1st line
            self.lcd_string(Line2, 0xC0)  # LCD RAM address for the 2nd line

    def lcd_byte(self,bits, mode):

        GPIO.output(self.__RS, mode)  # RS

        # High bits
        GPIO.output(self.__D4, False)
        GPIO.output(self.__D5, False)
        GPIO.output(self.__D6, False)
        GPIO.output(self.__D7, False)
        if bits & 0x10 == 0x10:
            GPIO.output(self.__D4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(self.__D5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(self.__D6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(self.__D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

        # Low bits
        GPIO.output(self.__D4, False)
        GPIO.output(self.__D5, False)
        GPIO.output(self.__D6, False)
        GPIO.output(self.__D7, False)
        if bits & 0x01 == 0x01:
            GPIO.output(self.__D4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(self.__D5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(self.__D6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(self.__D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()


    def lcd_toggle_enable(self):
        # Toggle enable
        time.sleep(0.0005)
        GPIO.output(self.__E, True)
        time.sleep(0.0005)
        GPIO.output(self.__E, False)
        time.sleep(0.0005)


    def lcd_string(self,message, line):
        message = message.ljust(self.__LCD_WIDTH, " ")

        self.lcd_byte(line, False)

        for i in range(self.__LCD_WIDTH):
            self.lcd_byte(ord(message[i]), True)

    def off(self):
        self.lcd_byte(0x01, False)  # 000001 Clear display
        time.sleep(0.5)
        self.lcd_byte(0x0B, False)  #display off

    def clear(self):
        self.lcd_byte(0x01, False)
        time.sleep(0.5)

def get_IP(network):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', bytes(network[:15], 'utf-8'))
    )[20:24])

db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="lex5690",
                         db="weatherstationdeluxe")

def get_data_from_db(sensor):
    cursor = db.cursor()
    sql = '''SELECT value FROM history as s1 WHERE time=(SELECT MAX(time) FROM history as s2 WHERE s1.sensorID = s2.sensorID) AND sensorID={0}'''.format(sensor)
    db.begin()
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    return data[0]

def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LCD_RS, GPIO.OUT)  # E
    GPIO.setup(LCD_E, GPIO.OUT)  # RS
    GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
    GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
    GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
    GPIO.setup(LCD_D7, GPIO.OUT)  # DB7
    lcd1 = LCD(LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7)
    while condition == True:
        lcd1.write_text("{0}".format(get_IP("wlan0")),"{0}:{1:.2f}C".format("temp",float(get_data_from_db(1))))
        time.sleep(2)
        lcd1.write_text("{0}".format(get_IP("wlan0")),"{0}:{1:.2f}hPA ".format("press",float(get_data_from_db(2))))
        time.sleep(2)
        lcd1.write_text("{0}".format(get_IP("wlan0")),"{0}:{1:.2f} %".format("humidity",float(get_data_from_db(3))))
        time.sleep(2)
        val1 = int(get_data_from_db(4))
        if val1 < 4:
            res1 = "Low"
        elif val1 < 7:
            res1 = "Oke"
        else:
            res1 = "High"
        lcd1.write_text("{0}".format(get_IP("wlan0")),"{0}:{1} {2}".format("UV-index",val1,res1))
        time.sleep(2)
        lcd1.write_text("{0}".format(get_IP("wlan0")),"{0}:{1} lux".format("light",get_data_from_db(5)))
        time.sleep(2)
        val2 = int(get_data_from_db(6))
        if val2 == 1:
            res2 = "None"
        elif val2 == 2:
            res2 = "Little"
        else:
            res2 = "Alot"
        lcd1.write_text("{0}".format(get_IP("wlan0")),"{0}:{1}".format("rainfall",res2))
        time.sleep(2)
        lcd1.write_text("{0}".format(get_IP("wlan0")),"{0}:{1:.2f} m/s".format("wind", float(get_data_from_db(7))))
        time.sleep(2)
    GPIO.cleanup()


if __name__ == '__main__':
    main()