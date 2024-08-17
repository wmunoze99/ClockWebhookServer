from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def colors_pickers():
    markup = InlineKeyboardMarkup()

    markup.row(*[InlineKeyboardButton("🔴 Red", callback_data="color_255,0,0"),
                 InlineKeyboardButton("🟠 Orange", callback_data="color_255,121,0"),
                 InlineKeyboardButton("🟡 Yellow", callback_data="color_255,255,0")])

    markup.row(*[InlineKeyboardButton("🟢 Green", callback_data="color_0,255,0"),
                 InlineKeyboardButton("🔵 Blue", callback_data="color_0,0,255"),
                 InlineKeyboardButton("🟣 Purple", callback_data="color_106,13,173")])

    return markup
