import telepot
import time 
WELCOME='Welcome to the Wanderers Bot,The Best Tour Guide.\nThis bot tells you the best and most relevant information. To start enter the name of place or type like <Place Agra> in this format or type <questions> for getting help you to suggest some places.'

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
    return


bot=telepot.Bot('*****ENTER BOT KEY***********')
bot.getMe()
bot.message_loop(handle)
print 'Listening.....'
while 1:
    time.sleep(5)
