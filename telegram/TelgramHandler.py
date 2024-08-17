import logging
import os
import telebot

from datetime import datetime
from telebot.types import BotCommand

from custom_markups.devices import devices_markup, bright_markup
from custom_markups.time import create_hour_selector, create_am_pm, create_minutes_selector
from store.hourStore import HourStore
from custom_markups.colors import colors_pickers
from websocket.socket import WebSocketManager
from dotenv import load_dotenv
from websocket.response import Response
from store.tunnel import MessageQueue

load_dotenv()

telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not telegram_token:
    raise Exception('TELEGRAM_TOKEN is not set')


socket_manager = WebSocketManager()
bot = telebot.TeleBot(telegram_token, parse_mode="MARKDOWN")


def listener(message: dict):
    logging.info(message)
    chat_id = message['chat_id']
    received_message = message['message']
    markup = message['markup']

    send_message_to(chat_id, received_message, markup)


mq = MessageQueue()


mq.listen('telegram', listener)


def init():
    bot.set_my_commands([
        BotCommand("login", "Login user on the device"),
        BotCommand("start", "Initialize bot and get a welcome message"),
        BotCommand("help", "Get help"),
        BotCommand("set_time", "Set the time for the clock"),
        BotCommand("setconfig", "Set the configuration for the clock"),
        BotCommand("set_color", "set the color of the clock"),
        BotCommand("set_brightness", "Set a new brightness to the clock")
    ], telebot.types.BotCommandScope())

    bot.set_my_commands([
        BotCommand("login", "Login user on the device"),
        BotCommand("start", "Initialize bot and get a welcome message"),
        BotCommand("help", "Get help"),
        BotCommand("set_time", "Set the time for the clock"),
        BotCommand("set_config", "Set the configuration for the clock"),
        BotCommand("set_color", "set the color of the clock"),
        BotCommand("set_brightness", "Set a new brightness to the clock")
    ], telebot.types.BotCommandScope(), 'en')

    bot.set_my_commands([
        BotCommand("login", "디바이스에서 로그인 사용자"),
        BotCommand("start", "봇 초기화 및 환영 메시지 받기"),
        BotCommand("help", "도움 받기"),
        BotCommand("set_time", "시계 시간 설정"),
        BotCommand("set_config", "시계 설정 구성"),
        BotCommand("set_color", "시계 색상 설정"),
        BotCommand("set_brightness", "시계에 새로운 밝기 설정")
    ], telebot.types.BotCommandScope(), 'ko')


@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, 'Welcome to your bot! From here you are able to control your clock\n **사랑헤** ❤️')


@bot.message_handler(commands=["login"])
def login(message):
    bot.reply_to(message, "Sure I will start login process")
    if len(socket_manager.connected_clients) == 0:
        bot.send_message(message.chat.id, "There is no devices yet")
    else:
        clients = WebSocketManager().connected_clients.keys()
        bot.send_message(message.chat.id, "Please select an available device to start the authentication",
                         reply_markup=devices_markup(clients))


@bot.message_handler(commands=["set_color"])
def set_color(message):
    bot.reply_to(message, "Select a color", reply_markup=colors_pickers())


@bot.message_handler(commands=['set_time'])
def set_time(message):
    today_utc = datetime.utcnow().date()
    bot.reply_to(message, f"Today is {today_utc} on UTC timezone")

    bot.send_message(message.chat.id, "Please select the current hour", reply_markup=create_hour_selector())
    bot.register_next_step_handler(message, process_time)


@bot.message_handler(commands=['set_brightness'])
def set_brightness(message):
    bot.send_message(message.chat.id, "Select a bright for the clock", reply_markup=bright_markup())


@bot.callback_query_handler(lambda call: call.data.startswith('bright'))
def selected_bright(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bright = str(call.data.split('_')[1])
    mq.add_message('websocket', {
        "chat_id": call.message.chat.id,
        "message": {
            "command": "set_bright",
            "bright": bright
        }
    })
    bot.send_message(call.message.chat.id, "Bright change")


@bot.callback_query_handler(lambda call: call.data.startswith('color_'))
def color_pick(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    color = str(call.data.split('_')[1])
    colors = color.split(',')
    r = int(colors[0])
    g = int(colors[1])
    b = int(colors[2])

    mq.add_message('websocket', {
        "chat_id": call.message.chat.id,
        "message": {
            "command": "set_color",
            "color": {
                "r": r,
                "g": g,
                "b": b
            }
        }
    })
    bot.send_message(call.message.chat.id, "Color change")


@bot.callback_query_handler(lambda call: call.data.startswith('device_'))
def auth_device(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    device = str(call.data.split('_')[1])
    response = Response("auth", {"mac": device, "chat_id": call.message.chat.id})
    socket_manager.send_message(device, response)
    bot.send_message(call.message.chat.id, f"Auth request send to device {device}")


@bot.callback_query_handler(lambda call: call.data.startswith('hour_'))
def process_time(call):
    store = HourStore()
    hour = int(call.data.split('_')[1])
    store.set_response_hour(hour)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"{hour}(AM or PM)?", reply_markup=create_am_pm())


@bot.callback_query_handler(lambda call: call.data.startswith('meridian_'))
def process_time(call):
    store = HourStore()
    meridian = call.data.split('_')[1]
    store.set_response_meridian(meridian)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    formated_hour = f"{store.get_response_hour()}:?? {store.get_response_meridian()}"
    bot.send_message(call.message.chat.id, f"Now the minutes \n {formated_hour}",
                     reply_markup=create_minutes_selector())


@bot.callback_query_handler(lambda call: call.data.startswith('minute_'))
def process_time(call):
    store = HourStore()
    minute = int(call.data.split('_')[1])
    store.set_response_minute(minute)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    formated_time = f"{store.get_response_hour()}:{store.get_response_minute()} {store.get_response_meridian()}"
    mq.add_message('websocket', {
        "chat_id": call.message.chat.id,
        "message": {
            "command": "set_time",
            "time": store.get_time()
        }
    })
    bot.send_message(call.message.chat.id, f"New time is {formated_time}")


@bot.callback_query_handler(lambda call: call.data.startswith('code_'))
def process_code_selection(call):
    data = call.data.split('_')
    mac = data[1]
    code = data[3]
    client = socket_manager.connected_clients[mac]
    bot.delete_message(call.message.chat.id, call.message.message_id)

    if int(client.code) == int(code):
        client.auth = True
        bot.send_message(call.message.chat.id, "Auth successfully ✅")
        bot.send_message(call.message.chat.id, f"Now you can send messages to this device {mac}")
    else:
        client.code = 0
        bot.send_message(call.message.chat.id, "Auth failed, try again ❌")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"{message.text} is not and allowed please use a command from the menu 😃")


def run():
    bot.infinity_polling()


def stop():
    bot.stop_polling()


def send_message_to(chat_id, message, markup=None):
    bot.send_message(chat_id, message, reply_markup=markup)
