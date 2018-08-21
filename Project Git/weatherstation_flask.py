import os
from flask import Flask, render_template, redirect, url_for ,request, flash, json
from DbClass import DbClass
from DbClass import get_last_temp, get_last_pressure, get_last_humidity,get_last_uvindex,get_last_light,get_last_rain,get_last_windspeed, time_format
from DbClass import history_temperature_format, history_airpressure_format, history_humidity_format, history_uv_index_format, history_light_index_format, history_rainfall_format, history_windspeed_format

app = Flask(__name__)
mysql = DbClass()

@app.route("/")
def base():
    weather_list = get_db_data()
    title = "Temperature"
    return render_template("base.html", weather_data = weather_list, history_val=history_temperature_format(),
                           history_time=time_format(),
                           title=title)

@app.route("/weatherstation")
def base2():
    weather_list = get_db_data()
    title = "Temperature"
    return render_template("base.html", weather_data=weather_list, history_val=history_temperature_format(),
                           history_time=time_format(),
                           title=title)

@app.route("/weatherstation/temperature")
def temperature():
    weather_list = get_db_data()
    title = "Temperature"
    return render_template("base.html", weather_data=weather_list, history_val=history_temperature_format(),
                           history_time=time_format(),
                           title=title)

@app.route("/weatherstation/airpressure")
def airpressure():
    weather_list = get_db_data()
    title = "Airpressure"
    return render_template("base.html", weather_data = weather_list, history_val=history_airpressure_format(),
                           history_time=time_format(),
                           title=title)

@app.route("/weatherstation/humidity")
def humidity():
    weather_list = get_db_data()
    title = "Humidity"
    return render_template("base.html", weather_data = weather_list, history_val=history_humidity_format(),
                           history_time=time_format(),
                           title=title)

@app.route("/weatherstation/uvindex")
def uvindex():
    weather_list = get_db_data()
    title = "UV-index"
    return render_template("base.html", weather_data=weather_list, history_val=history_uv_index_format(),
                           history_time=time_format(),
                           title=title)

@app.route("/weatherstation/lightindex")
def lightindex():
    weather_list = get_db_data()
    title = "Light-index"
    return render_template("base.html", weather_data=weather_list, history_val=history_light_index_format(),
                           history_time=time_format(),
                           title=title)

@app.route("/weatherstation/rainfall")
def rainfall():
    weather_list = get_db_data()
    title = "Rainfall [1 = low / 2 = light rain / 3 = heavy rain]"
    return render_template("base.html", weather_data=weather_list, history_val=history_rainfall_format(),
                           history_time=time_format(),
                           title=title)

@app.route("/weatherstation/windspeed")
def windspeed():
    weather_list = get_db_data()
    title = "Windspeed"
    return render_template("base.html", weather_data=weather_list, history_val=history_windspeed_format(),
                           history_time=time_format(),
                           title=title)

def get_db_data():
    data = []
    data.append(get_last_temp())
    data.append(get_last_pressure())
    data.append(get_last_humidity())
    data.append(get_last_uvindex())
    data.append(get_last_light())
    data.append(get_last_rain())
    data.append(get_last_windspeed())
    return data


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')