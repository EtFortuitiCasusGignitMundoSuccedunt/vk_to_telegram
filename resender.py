#! /usr/bin/python3

import os, configparser, telebot
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, threading, re

pwd = os.environ['HOME']+'/.config/vk_to_telegram'
config = configparser.ConfigParser()
config.read(pwd+'/config')
bot_token = config.get('General', 'bot_token')
send_ids = config.get('General', 'user_ids')
send_ids = [x.strip("[] '") for x in send_ids.split(',')]
bot = telebot.TeleBot(bot_token)

def bot_send(msg):
    if msg == "Ohhh... there are some errors: 'ts'": # This blocks notification that VkLongPoll restarted
        return
    for i in send_ids:
        bot.send_message(i, msg)

def ParseAtta(msg):
    attachments = []
    for i in msg['attachments']:
        print(i)
        print()
        if i['type'] == 'sticker':
            sticker = i['sticker']
            maxq = 0
            for j in sticker['images']:
                if j['width']*j['height']>maxq:
                    maxq = j['width']*j['height']
                    url = j['url']
            attachments.append('sticker {}'.format(url))
        elif i['type'] == 'photo':
            maxq = 0
            for j in i['photo']['sizes']:
                if j['width']*j['height']>maxq:
                    maxq = j['width']*j['height']
                    url = j['url']
            attachments.append('photo {}'.format(url))
        elif i['type'] == 'audio_message':
            attachments.append('voice message '+i['audio_message']['link_ogg'])
        elif i['type'] == 'doc':
            attachments.append('document '+i['doc']['url'])
        elif i['type'] == 'wall':
            attachments.append('wall https://vk.com/wall{}_{}'.format(i['wall']['from_id'], i['wall']['id']))
        elif i['type'] == 'video':
            attachments.append('video '+i['video']['player'])
        else:
            attachments.append(str(i))
    print(attachments)
    return attachments

def ParseRepl(msg, api, fwd_level=1):
    bot_send('| '*(fwd_level-1)+'\\_'+'\tReply: ')
    reply = msg['reply_message']
    print(reply)
    print()
    print()
    user = api.users.get(user_ids=reply['from_id'])[0]
    bot_send('| '*fwd_level+'\tfrom "{} {}": '.format(user['first_name'], user['last_name']) + reply['text'])
    if 'attachments' in reply.keys():
        if reply['attachments']!=[]:
            attachments = ParseAtta(reply)
            bot_send('|'*fwd_level+'\tattachments: '+attachments[0])
            for i in attachments[1:]:
                bot_send(i)
    if 'fwd_messages' in reply.keys():
        if reply['fwd_messages']!=[]:
            ParseForw(reply, api, fwd_level+1)
    print()
    print()

def ParseForw(msg, api, fwd_level=1):
    bot_send('| '*(fwd_level-1)+'\\_'+'\tForwards: ')
    for i in msg['fwd_messages']:
        print(i)
        print()
        print()
        user = api.users.get(user_ids=i['from_id'])[0]
        bot_send('| '*fwd_level+'\tfrom "{} {}": '.format(user['first_name'], user['last_name']) + i['text'])
        if 'attachments' in i.keys():
            if i['attachments']!=[]:
                attachments = ParseAtta(i)
                bot_send('|'*fwd_level+'\tattachments: '+attachments[0])
                for j in attachments[1:]:
                    bot_send(j)
        if 'reply_message' in i.keys():
            if i['reply_message']!=[]:
                ParseRepl(i, api, fwd_level+1)
        if 'fwd_messages' in i.keys():
            if i['fwd_messages']!=[]:
                ParseForw(i, api, fwd_level+1)
        print()
        print()

def ParsePriv(msg, me, user, api):
    print(msg)
    print()
    print()
    bot_send('Sent from "{} {}" message to "{} {}": '.format(user['first_name'], user['last_name'], me['first_name'], me['last_name']) + msg['text'])
    if msg['attachments']!=[]:
        attachments = ParseAtta(msg)
        bot_send('Attachments: '+attachments[0])
        for i in attachments[1:]:
            bot_send(i)
    if 'reply_message' in msg.keys():
        if msg['reply_message']!=[]:
            ParseRepl(msg, api)
    if msg['fwd_messages']!=[]:
        ParseForw(msg, api)
    print()
    print()

def ParseChat(msg, me, user, api):
    chat = api.messages.getChat(chat_id=msg['peer_id']-2000000000)
    print(msg, chat)
    print()
    print()
    bot_send('In chat "{}" sent from "{} {}" message to "{} {}": '.format(chat['title'], user['first_name'], user['last_name'], me['first_name'], me['last_name']) + msg['text'])
    if msg['attachments']!=[]:
        attachments = ParseAtta(msg)
        bot_send('Attachments: '+attachments[0])
        for i in attachments[1:]:
            bot_send(i)
    if 'reply_message' in msg.keys():
        if msg['reply_message']!=[]:
            ParseRepl(msg, api)
    if msg['fwd_messages']!=[]:
        ParseForw(msg, api)
    print()
    print()

class LongPool(threading.Thread):

    def __init__(self, account):
        threading.Thread.__init__(self)
        self.paused = False
        self.token = account[0]
        self.chat_users = account[1]
        self.chats = account[2]

    def run(self):
        session = vk_api.VkApi(token=self.token, api_version='5.92')
        api = session.get_api()
        me = api.users.get()[0]
        print('Bot have started for "{} {}"'.format(me['first_name'], me['last_name']))
        while 1:
            long_pooll = VkLongPoll(session)
            try:
                for i in long_pooll.listen():
                    if self.paused:
                        continue
                    if i.type == VkEventType.MESSAGE_NEW:
                        msg_ext = api.messages.getById(message_ids=i.message_id)
                        msg = msg_ext['items'][0]
                        if msg['from_id']<0:
                            continue
                        user = api.users.get(user_ids=msg['from_id'])[0]
                        if msg['out']:
                            continue
                        if str(msg['peer_id']-2000000000) in self.chats:
                           ParseChat(msg, me, user, api)
                        elif msg['peer_id']-2000000000 < 0 and '*' in self.chat_users:
                            ParsePriv(msg, me, user, api)
                        elif msg['peer_id']-2000000000 < 0 and str(msg['from_id']) in self.chat_users:
                            ParsePriv(msg, me, user, api)

            except Exception as exep:
                bot_send('Ohhh... there are some errors: '+str(exep))

    def stop(self):
        self.paused = True

    def resume(self):
        self.paused = False

@bot.message_handler(commands=['start'])
def handle_start(message):
    for i in threads:
        i.resume()
    for i in send_ids:
        bot.send_message(i, 'Bot have resumed')

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    for i in threads:
        i.stop()
    for i in send_ids:
        bot.send_message(i, 'Bot have stoped')
@bot.message_handler(commands=['kill'])
def kill(message):
    for i in send_ids:
        bot.send_message(i, 'Bot have been killed')
    *proc, = os.popen('ps axu | grep resender.py')
    pid = proc[0].split()[1]
    os.system('kill '+pid)

accounts = [i.strip("[]' ") for i in config.get('General', 'vk_users').split(',')]
check_configs = []
for name in accounts:
    check_configs.append([config.get(name, 'token'), [i.strip("[] '") for i in config.get(name, 'chat_users').split(',')], [i.strip("[] '") for i in config.get(name, 'chats').split(',')]])

global threads
threads = []
for i in check_configs:
    threads.append(LongPool(i))
    threads[-1].start()

while 1:
    try:
        bot.polling(none_stop=True)
    except Exception as exep:
        bot_send('Ohhh... there are some errors: '+str(exep))
