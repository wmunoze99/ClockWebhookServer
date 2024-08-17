from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def devices_markup(clients):
    markup = InlineKeyboardMarkup()

    for client in clients:
        markup.row(InlineKeyboardButton(client, callback_data=f"device_{client}"))

    return markup


def bright_markup():
    markup = InlineKeyboardMarkup()

    markup.row(*[InlineKeyboardButton('5%', callback_data='bright_5'),
                 InlineKeyboardButton('10%', callback_data='bright_10'),
                 InlineKeyboardButton('25%', callback_data='bright_25'),
                 InlineKeyboardButton('50%', callback_data='bright_50'),
                 InlineKeyboardButton('80%', callback_data='bright_80'),
                 InlineKeyboardButton('100%', callback_data='bright_100')])

    return markup