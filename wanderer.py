import telepot
import time
import urllib2
import json
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import datetime
import re
WELCOME='Welcome to the Wanderers Bot,The Best Tour Guide.\nThis bot tells you the best and most relevant information. To start enter the name of place or type like <Place Agra> in this format or type <questions> for getting help you to suggest some places.'
airportdict={'Agartala':'IXA','Agra':'AGR','Ahmedabad':'AMD','Allahabad':'IXD','Amritsar':'ATQ','Aurangabad':'IXU','Bagdogra':'IXB','Banglore':'BLR','Bhavnagar':'BHU','Bhopal':'BHO','Bhubaneswar':'BBI','Bhuj':'BHJ','Kolkata':'CCU','Chandigarh':'IXC','Chennai':'MAA','Cochin':'COK','Coimbatore':'CJB','Daman':'NMB','Dehradun':'DED',
          'Dibrugarh':'DIB','Dimapur':'DMU','Diu':'DIU','Gauhati':'GAU','Goa':'GOI','Gwalior':'GWL','Hubli':'HBX','Hyderabad':'HYD','Imphal':'IMF','Indore':'IDR','Jaipur':'JAI','Jammu':'IXJ','Jamnagar':'JGA','Jamshedpur':'IXW','Jodhpur':'JDH','Jorhat':'JRH','Kanpur':'KNU','Khajuraho':'HJR','Kozhikode':'CCJ','Leh':'IXL','Lucknow':'LKO','Ludhiana':'LUH','Madurai':'IXM','Manglore':'IXE','Mumbai':'BOM','Nagpur':'NAG','Nanded':'NDC','Nasik':'ISK','New Delhi':'DEL',
             'Patna':'PAT','Pondicherry':'PNY','Pune':'PNQ','Porbandar':'PBD','Port Blair':'IXZ','Puttaparthi':'PUT','Rae Bareli':'BEK','Rajkot':'RAJ','Ranchi':'IXR','Shillong':'SHL','Silchar':'IXS','Srinagar':'SXR','Surat':'STV','Tezpur':'TEZ','Tiruchirapally':'TRZ','Tirupati':'TIR','Trivandrum':'TRV','Udaipur':'UDR','Vadodra':'BDQ','Varanasi':'VNS','Vijyawada':'VGA','Vishakhapatnam':'VTZ'}
def sendManual(msg):
    chat_id=msg['from']['id']
    #sendRatebyRailway(msg) #correct this function
    sendRatebyRoad(msg)
    sendRatebyAir(msg)
    return
def sendRatebyRailway(msg):
    username=msg['from']['first_name']
    chat_id=msg['from']['id']
    command=msg['text']
    count=0
    place=command.split()[1]
    date=command.split()[2]
    print(place)
    print(date)
    url='http://api.railwayapi.com/between/source/ndls/dest/%s/date/%s/apikey/0zwjh5be'%(place,date)
    print url
    numberdata=urllib2.urlopen(url)
    response=json.load(numberdata)
    for x in range(len(response['train'])):
        count=count+1
        if count>10:
            break
        else:
            number=response['train'][x]['number']
            print number
            calculateRate(number,place,date,chat_id)
    return

def calculateRate(number,place,date,chat_id):
    url1='http://api.railwayapi.com/fare/train/%s/source/ndls/dest/%s/age/20/quota/GEN/doj/%s/apikey/0zwjh5be'%(number,place,date)
    print url1 
    faredata=urllib2.urlopen(url1)
    response=json.load(faredata)
    s1=""
    for x in range(len(response['fare'])):
        if response['fare'][x]['fare'] is not s1:
            classname=response['fare'][x]['name']
            fare=response['fare'][x]['fare']
            bot.sendMessage(chat_id,'%s %s %s Rs'%(response['train']['name'],classname,fare))
    return
def sendRatebyRoad(msg):
    chat_id=msg['from']['id']
    command=msg['text']
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
    print(great_circle(a,b).kilometers)
    distance=great_circle(a,b).kilometers
    print distance
    litres=distance/18
    litres2=distance/12
    costdiesel=litres*55
    costpetrol=litres2*65
    bot.sendMessage(chat_id,'Details for travelling by road:')
    bot.sendMessage(chat_id,'Rate of diesel for car giving 18 average-%d Rs(approx)'%(costdiesel))
    bot.sendMessage(chat_id,'Rate of petrol for car giving 12 average-%d Rs(approx)'%(costpetrol))
    return

def sendRatebyAir(msg):
    code='cod'
    chat_id=msg['from']['id']
    command=msg['text']
    pos=command.index('to')
    placefrom=command[5:pos]
    print placefrom
    m=re.search("\d",command)
    num=m.start()
    placeto=command[pos+2:num]
    print placeto
    g=len(command)
    date=command[num:g]
    print date
    for key,value in airportdict.iteritems():
        if key in placefrom:
            code1=value
            print code1
            break
    for key,value in airportdict.iteritems():
        if key in placeto:
            code=value
            print code
            break
    date=datetime.datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
    print code
    BASE_URL='https://flight.yatra.com/air-lowest-fares/dom2/getFares?origin=%s&destination=%s&startDate=%s'%(code1,code,date)
    print BASE_URL
    data=urllib2.urlopen(BASE_URL)
    response=json.load(data)
    print len(response[0])
    if len(response[0])==0:
        bot.sendMessage(chat_id,'No flights available on this day')
    else:
        bot.sendMessage(chat_id,'Your flight details are:')
        print response[0]['mnArr'][0]['cf'][0]['yan']
        for x in range(len(response[0]['mnArr'][0]['cf'])):
            yan=response[0]['mnArr'][0]['cf'][x]['yan']
            dt=response[0]['mnArr'][0]['cf'][x]['dt']
            at=response[0]['mnArr'][0]['cf'][x]['at']
            tf=response[0]['mnArr'][0]['cf'][x]['tf']
            bot.sendMessage(chat_id,'%s - Departure at %s arrival at %s\n FARE-%sRs'%(yan,dt,at,tf))
    return

def handle(msg):
    print 'Message is ',msg
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type)
    username=msg['from']['first_name']
    chat_id=msg['from']['id']
    command=msg['text']
    if command == '/start':
        bot.sendMessage(chat_id,WELCOME)
    if command=='questions':
        #QUESTIONS PART
        print 'ASK QUES'
    if command.split(' ',1)[0]=='Place':
        print 'WELCOME FINALLY'
        sendManual(msg)
    return


bot=telepot.Bot('******************BOT KEY****************************')
bot.getMe()
bot.message_loop(handle)
print 'Listening.....'
while 1:
    time.sleep(5)
