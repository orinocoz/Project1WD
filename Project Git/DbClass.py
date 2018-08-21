import MySQLdb

class DbClass:
    def __init__(self):
        self.__db = MySQLdb.connect(host="localhost",
                                 user="root",
                                 passwd="lex5690",
                                 db="weatherstationdeluxe")

    def get_last_data(self, sensor):
        sql = '''SELECT value FROM history as s1 WHERE time=(SELECT MAX(time) FROM history as s2 WHERE s1.sensorID = s2.sensorID) AND sensorID={0}'''.format(sensor)
        cursor = self.__db.cursor()
        self.__db.begin()
        cursor.execute(sql)
        data = cursor.fetchone()
        cursor.close()
        return data

    def get_history(self, sensor):
        sql = '''SELECT value FROM history as s1 WHERE sensorID={0} ORDER BY time DESC LIMIT 30'''.format(
            sensor)
        cursor = self.__db.cursor()
        self.__db.begin()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_time(self, sensor):
        sql = '''SELECT time FROM history as s1 WHERE sensorID={0} ORDER BY time DESC LIMIT 30'''.format(sensor)
        cursor = self.__db.cursor()
        self.__db.begin()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        return data

db = DbClass()

def get_last_temp():
    value = db.get_last_data(1)
    value = float(value[0])
    value = round(value, 1)
    return value

def get_last_pressure():
    value = db.get_last_data(2)
    value = float(value[0])
    value = round(value, 2)
    return value

def get_last_humidity():
    value = db.get_last_data(3)
    value = float(value[0])
    value = round(value, 2)
    return value

def get_last_uvindex():
    value = db.get_last_data(4)
    value = value[0]
    return value

def get_last_light():
    value = db.get_last_data(5)
    value = value[0]
    return value

def get_last_rain():
    value = db.get_last_data(6)
    value = value[0]
    if value == "1":
        res = "None"
    elif value == "2":
        res = "Little"
    else:
        res = "Alot"
    return res

def get_last_windspeed():
    value = db.get_last_data(7)
    value = float(value[0])
    value = round(value, 2)
    return value

def get_history_temp():
    value = db.get_history(1)
    return value

def get_history_pressure():
    value = db.get_history(2)
    return value

def get_history_humidity():
    value = db.get_history(3)
    return value

def get_history_uvindex():
    value = db.get_history(4)
    return value

def get_history_light():
    value = db.get_history(5)
    return value

def get_history_rain():
    value = db.get_history(6)
    return value

def get_history_windspeed():
    value = db.get_history(7)
    return value

def time_format():
    history_time = db.get_time(1)
    data = []
    for i in range(29, 0, -1):
        data.append(str(history_time[i][0]))
    return data

def history_temperature_format():
    history_temp = get_history_temp()
    data = []
    for i in range(29, 0, -1):
        data.append(str(history_temp[i][0]))
    return data

def history_humidity_format():
    history_humidity = get_history_humidity()
    data = []
    for i in range(29, 0, -1):
        data.append(str(history_humidity[i][0]))
    return data

def history_airpressure_format():
    history_pressure = get_history_pressure()
    data = []
    for i in range(29, 0, -1):
        data.append(str(history_pressure[i][0]))
    return data

def history_uv_index_format():
    history_uvindex = get_history_uvindex()
    data = []
    for i in range(29, 0, -1):
        data.append(str(history_uvindex[i][0]))
    return data

def history_light_index_format():
    history_lightindex = get_history_light()
    data = []
    for i in range(29, 0, -1):
        data.append(str(history_lightindex[i][0]))
    return data

def history_rainfall_format():
    history_rain = get_history_rain()
    data = []
    for i in range(29, 0, -1):
        data.append(str(history_rain[i][0]))
    return data

def history_windspeed_format():
    history_windspeed = get_history_windspeed()
    data = []
    for i in range(29, 0, -1):
        data.append(str(history_windspeed[i][0]))
    return data

