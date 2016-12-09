import telepot
import time
import urllib2
import json
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import datetime
import re
from airports import airportdict
from stations import stationdict
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

destinations = {}

WELCOME='Welcome to the Wanderers Bot,The Best Tour Guide.\nThis bot tells you the best and most relevant information. To start enter the name of place or type like <Place Agra> in this format or type <questions> for getting help you to suggest some places.'

def sendManual(msg):
    chat_id=msg['from']['id']
    getRailwayData(msg)
    sendRatebyRoad(msg)
    sendRatebyAir(msg)
    return

def sendTrainData(chat_id, station_name):
    global destinations
    res = destinations[int(chat_id)].split("QQQ")
    destination = res[0]
    date = res[1]
    date = datetime.datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
    stations_url = "https://www.yatra.com/trains/b2c/autosuggestion?q=%s&limit=100&url="%(destination)
    data = urllib2.urlopen(stations_url).read()
    pattern = re.compile("\s[A-Z]+:")
    result = re.findall(pattern, data)
    train_data_url = "https://rail.yatra.com/trains/b2c/ajax-search?departDate=%s&destStn=%s&srcStn=%s"%(date, result[0][:-1].strip(), station_name)
    response = json.load(urllib2.urlopen(train_data_url))
    response = response["finalTrainListResJson"]["trainBtwnStnsList"]
    for resp in response:
        bot.sendMessage(chat_id, "%s - Departure at %s, Arrival at %s"%(resp["trainName"], resp["departureTime"], resp["arrivalTime"]))

def getRailwayData(chat_id, command):
    global destinations
    pos=command.index('to')
    placefrom=command[5:pos].lower().strip()
    m=re.search("\d",command)
    placeto=command[pos+2:m.start()].lower().strip()
    date = command[m.start():].strip()
    destinations.update({int(chat_id): placeto+"QQQ"+date})
    # print destinations
    stations_url = "https://www.yatra.com/trains/b2c/autosuggestion?q=%s&limit=100&url="%(placefrom)
    data = urllib2.urlopen(stations_url).read()
    pattern = re.compile("\s[A-Z]+:")
    result = re.findall(pattern, data)
    if len(result) == 0:
        bot.sendMessage(chat_id,'No railway stations available in the area mentioned')
        return
    keyboard = {'keyboard': [], 'resize_keyboard': True, 'callback_data': 'hello'}
    for i in range(len(result)):
        result[i] = result[i].strip()[:-1]
        list = keyboard["keyboard"]
        try:
            list.append([result[i] + "(" + stationdict[result[i]] + ")"])
        except:
            pass
        keyboard.update({"keyboard": list})
    # keyboard = InlineKeyboardMarkup(inline_keyboard=[list(map(lambda station: InlineKeyboardButton(text=station, callback_data=station), result))])
    bot.sendMessage(chat_id, 'Select a station: ', reply_markup=keyboard)

def sendRatebyRoad(chat_id, command):
    pos=command.index('to')
    placefrom=command[5:pos]
    m=re.search("\d",command)
    placeto=command[pos+2:m.start()]
    placefrom=placefrom.strip()
    placeto=placeto.strip()
    #print placefrom
    #print placeto
    geolocator=Nominatim()
    location=geolocator.geocode(placefrom)
    lat=location.latitude
    lon=location.longitude
    location1=geolocator.geocode(placeto)
    lat1=location1.latitude
    lon1=location1.longitude
    a=(lat,lon)
    b=(lat1,lon1)
    # print(great_circle(a,b).kilometers)
    distance=great_circle(a,b).kilometers
    # print distance
    litres=distance/18
    litres2=distance/12
    costdiesel=litres*55
    costpetrol=litres2*65
    bot.sendMessage(chat_id,'Details for travelling by road:')
    bot.sendMessage(chat_id,'Rate of diesel for car giving 18 average-%d Rs(approx)'%(costdiesel))
    bot.sendMessage(chat_id,'Rate of petrol for car giving 12 average-%d Rs(approx)'%(costpetrol))
    return

def sendRatebyAir(chat_id, command):
    code='cod'
    code1=None
    pos=command.index('to')
    placefrom=command[5:pos].lower().strip()
    # print placefrom
    m=re.search("\d",command)
    num=m.start()
    placeto=command[pos+2:num].lower().strip()
    # print placeto
    g=len(command)
    date=command[num:g]
    # print date
    for key,value in airportdict.iteritems():
        # print placefrom, key
        if placefrom in key:
            code1=value
            # print code1
            break
    for key,value in airportdict.iteritems():
        if placeto in key:
            code=value
            # print code
            break
    date=datetime.datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
    # print code
    BASE_URL='https://flight.yatra.com/air-lowest-fares/dom2/getFares?origin=%s&destination=%s&startDate=%s'%(code1,code,date)
    # print BASE_URL
    data=urllib2.urlopen(BASE_URL)
    response=json.load(data)
    # print len(response[0])
    if len(response[0])==0:
        bot.sendMessage(chat_id,'No flights available on this day')
    else:
        bot.sendMessage(chat_id,'Your flight details are:')
        # print response[0]['mnArr'][0]['cf'][0]['yan']
        for x in range(len(response[0]['mnArr'][0]['cf'])):
            yan=response[0]['mnArr'][0]['cf'][x]['yan']
            dt=response[0]['mnArr'][0]['cf'][x]['dt']
            at=response[0]['mnArr'][0]['cf'][x]['at']
            tf=response[0]['mnArr'][0]['cf'][x]['tf']
            bot.sendMessage(chat_id,'%s - Departure at %s arrival at %s\n FARE-%sRs'%(yan,dt,at,tf))
    return

def handle(msg):
    # print 'Message is ',msg
    # content_type, chat_type, chat_id = telepot.glance(msg)
    # print(content_type)

    if "data" in msg.keys():
        text = msg["data"].split('QQQ')
        if(text[0] == "Road"):
            sendRatebyRoad(text[1], text[2])
        elif(text[0] == "Train"):
            getRailwayData(text[1], text[2])
        elif(text[0] == "Air"):
            sendRatebyAir(text[1], text[2])
        return

    username=msg['from']['first_name']
    chat_id=msg['from']['id']
    command=msg['text']
    if command == '/start':
        bot.sendMessage(chat_id,WELCOME)
    if command=='questions':
        #QUESTIONS PART
        # print 'ASK QUES'
        pass
    if command.split(' ',1)[0]=='Place':
        # print 'WELCOME FINALLY'
        # sendManual(msg)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text = "Road", callback_data = "RoadQQQ"+str(chat_id)+"QQQ"+command),
            InlineKeyboardButton(text = "Train", callback_data = "TrainQQQ"+str(chat_id)+"QQQ"+command),
            InlineKeyboardButton(text = "Air", callback_data = "AirQQQ"+str(chat_id)+"QQQ"+command),
            ]])
        bot.sendMessage(chat_id, "Your mode of travel?", reply_markup = keyboard)
    if command[:command.find('(')] in stationdict.keys():
        sendTrainData(chat_id, command[:command.find('(')])
    return

bot=telepot.Bot('293905956:AAHm0W4lbumU1RuGZFJb22oLHwTfLcQYMLg')
bot.getMe()
bot.message_loop(handle)
print 'Listening.....'
while 1:
    time.sleep(5)
