import numpy as np
from flask import Flask, render_template, jsonify, request
import pymongo
import json
import httplib2

open_weather_map_API_key = "8bc98ed85ea557d3c95933a8372476c3"
open_weather_API_endpoint = "http://api.openweathermap.org/"

http_initializer = httplib2.Http()

city_names =['melbourne', 'toronto', 'suva']

def APItoMongoDB():
    # Initialize MongoDB client running on localhost
    client = pymongo.MongoClient('mongodb+srv://kt:ktmongo@bdat1004-db.fdmzu.mongodb.net/Project0?retryWrites=true&w=majority')

    # We create a collection for each city to store data
    for city in city_names:
        url = open_weather_API_endpoint + "/data/2.5/forecast?q=" + city + "&appid=" + open_weather_map_API_key
        http_initializer = httplib2.Http()
        response, content = http_initializer.request(url, 'GET')
        utf_decoded_content = content.decode('utf-8')
        json_object = json.loads(utf_decoded_content)
        print(json_object)

        # Creating Mongodb database
        db = client.weather_data

        # Putting Openweathermap API data in database, with timestamp as primary key
        for element in json_object["list"]:
            try:
                datetime = element['dt']
                del element['dt']
                db['{}'.format(city)].insert_one({'_id': datetime, "data": element})
            except pymongo.errors.DuplicateKeyError:
                continue
APItoMongoDB()

temperatures = {}
dayandtime = {}
feellike = {}
data = {}
def GetTempDataFromMongoDB():
    client = pymongo.MongoClient('mongodb+srv://kt:ktmongo@bdat1004-db.fdmzu.mongodb.net/Project0?retryWrites=true&w=majority')
    for city in city_names:
        temperatures[city] = []
        dayandtime[city] = []
        feellike[city] = []
    with client:
        db = client.weather_data
        for city in city_names:
            data = db['{}'.format(city)].find({})
            for record in data:
                first_time = True
                temp = round((record["data"]["main"]["temp"] - 273.15), 1)
                feels = round((record["data"]["main"]["feels_like"] - 273.15), 1)
                tempDate = record["data"]["dt_txt"]
                temperatures[city].append([temp])
                dayandtime[city].append([tempDate])
                feellike[city].append([feels])

GetTempDataFromMongoDB()

def FormatTData(city):
    #for city in city_names:
    globals()[str(city) + 'yValList'] = []
    globals()[str(city) + 'xValList'] = []
    for val in temperatures[city]:
        globals()[str(city) + 'yValList'].append(val[0])
    for val2 in dayandtime[city]:
        globals()[str(city) + 'xValList'].append(val2[0])
    x = (globals()[str(city) + 'xValList'])
    y = (globals()[str(city) + 'yValList'])
    i = len(globals()[str(city) + 'xValList'])
    data['Date'] = 'Temp'
        #data['Location'] = city
    counter2 = 0
    while counter2 < i:
        data[str(x[counter2])] = (y[counter2])
        counter2+=1
    return(data)
    #print(str(data))

def FormatTDifference(city):
    #for city in city_names:
    a = [item for sublist in temperatures[city] for item in sublist]
    b = [item for sublist in feellike[city] for item in sublist]
    difference = [y - x for x, y in zip(a, b)]
    np_array = np.array(difference)
    round = np.around(np_array, 1)
    round_to_tenths = list(map(lambda el:[el], round))
    globals()[str(city) + 'y1ValList'] = []
    globals()[str(city) + 'xValList'] = []
    for val in round_to_tenths:
        globals()[str(city) + 'y1ValList'].append(val[0])
    for val2 in dayandtime[city]:
        globals()[str(city) + 'xValList'].append(val2[0])
    x = (globals()[str(city) + 'xValList'])
    y = (globals()[str(city) + 'y1ValList'])
    i = len(globals()[str(city) + 'xValList'])
    data['Date'] = 'Temp'
    # data['Location'] = city
    counter2 = 0
    while counter2 < i:
        data[str(x[counter2])] = (y[counter2])
        counter2 += 1
    return(data)
    #print(str(data))

data2 = {}
def holiday():
    for city in city_names:
        a = [item for sublist in feellike[city] for item in sublist]
        average = sum(a) / len(a)
        ave = round(average,1)
        #print('The average feel-like temperature of ' + city.capitalize() + ' for the next 5 days will be ' + str(ave) + 'C°')
        data2[city] = ave
        # data['Location'] = city
    return (data2)
    #print(str(data2))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tweather')
def toronto():
    data = FormatTData('toronto')
    return render_template('tline.html', data=data)


@app.route('/mweather')
def melbourne():
    data = FormatTData('melbourne')
    return render_template('mline.html', data=data)

@app.route('/sweather')
def suva():
    data = FormatTData('suva')
    return render_template('sline.html', data=data)

@app.route('/mdif')
def mdif():
    data = FormatTDifference('melbourne')
    return render_template('mline1.html', data=data)

@app.route('/sdif')
def sdif():
    data = FormatTDifference('suva')
    return render_template('sline1.html', data=data)

@app.route('/tdif')
def tdif():
    data = FormatTDifference('toronto')
    return render_template('tline1.html', data=data)


if __name__ == '__main__':
    app.run()