from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_hour_selector():
    markup = InlineKeyboardMarkup()
    row = []

    for hour in range(12):
        _hour = (hour + 1)
        row.append(InlineKeyboardButton(str(_hour), callback_data=f"hour_{_hour}"))

        if len(row) == 6:
            markup.row(*row)
            row = []

    if row:
        markup.row(*row)

    return markup


def create_am_pm():
    markup = InlineKeyboardMarkup()
    markup.row(*[
        InlineKeyboardButton("AM", callback_data="meridian_AM"),
        InlineKeyboardButton("PM", callback_data="meridian_PM")
    ])

    return markup


def create_minutes_selector():
    markup = InlineKeyboardMarkup()
    row = []

    for minute in range(61):
        row.append(InlineKeyboardButton(str(minute), callback_data=f"minute_{minute}"))

        if len(row) == 6:
            markup.row(*row)
            row = []

    if row:
        markup.row(*row)

    return markup
