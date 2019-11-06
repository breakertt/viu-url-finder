# -*-coding:utf8-*-

# help - help info
# series - enter anime name
# episode - enter episode id in viu

import viu_info
import json
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


with open('config.json', 'r') as config:
    config_data = ""
    for line in config.readlines():
        config_data += line
    config_data = json.loads(config_data)    
    
bot = telebot.TeleBot(config_data['token'])

proxy = None
if 'proxy' in config_data:
    proxy = config_data['proxy']

def gen_markup_series(seriresData):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for i in range(len(seriresData)):
        callback_data_json = {
            "id" : seriresData[i]['product_id'],
            "type": 1
        }
        callback_data = json.dumps(callback_data_json)
        markup.add(InlineKeyboardButton(seriresData[i]['name'], callback_data=callback_data))
    return markup

def episodeHandler(chat_id,episode_id):
    epData = viu_info.episode(episode_id,proxy)
    epDataList = list(epData)
    if len(list(epData)) <= 1:
        bot.send_message(chat_id, "暂无结果")
    else:
        bot.send_message(chat_id, "番剧:" + epData['name'] + " 请选择集数:", reply_markup=gen_markup_eps(epData,epDataList))

def gen_markup_eps(epData,epDataList):
    markup = InlineKeyboardMarkup()
    count = 0
    list = []
    epDataList.reverse()
    for i in range(len(epDataList)):
        key = epDataList[i]
        value = epData[epDataList[i]]
        if key != 'name':
            callback_data_json = {
                "number" : value['number'],
                "type": 2
            }
            callback_data = json.dumps(callback_data_json)
            list.append(InlineKeyboardButton(text=callback_data_json["number"], url=value["link"],callback_data=callback_data))

            if (count % 5 == 4):
                markup.row(*list)
                list = []
            count += 1
                
    markup.row(*list)
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "本机器人可以帮助提供viu上视频的链接。")

@bot.message_handler(commands=['series'])
def message_handler(message):
    print(message.text)
    message_list = message.text.split()
    if len(message_list) == 1:
        bot.reply_to(message, "使用方法: /series <番剧名>")
    else:
        seriresData = viu_info.search(message.text[len(message_list[0])+1:len(message.text)],proxy)
        if len(seriresData) == 0:
            bot.reply_to(message, "无相关番剧")
        else:
            bot.send_message(message.chat.id, "请选择番剧:", reply_markup=gen_markup_series(seriresData))

@bot.message_handler(commands=['episode'])
def message_handler(message):
    message_list = message.text.split()
    if len(message_list) == 1:
        bot.reply_to(message, "使用方法: /episode <番剧id>")
    else:
        episodeHandler(message.chat.id, message_list[1])
        

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    callback_data_json = json.loads(call.data)
    if callback_data_json['type'] == 1:
        episodeHandler(call.message.chat.id, callback_data_json['id'])

bot.polling()