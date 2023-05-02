import telebot
import config

"""
import telepot
token = '6226679318:AAHypKT7bQFLgkwpK7gfcZ4W0WI1TvgzaYc'
TelegramBot = telebot.Bot(token)
print(TelegramBot.getMe())
print(TelegramBot.getUpdates()[0])
"""

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "Добро пожаловать, о новый пользователь!")

@bot.message_handler(commands=["help"])
def welcome(message):
    bot.send_message(message.chat.id, "Смотри, что я умею:")
    # нужно создать файл со списком комманд

@bot.message_handler(commands=["add_word"])
def add_word(message):
    bot.send_message(message.chat.id, "Введите слово:")
    

@bot.message_handler(content_types=["text"])
def answer(message):
    bot.send_message(message.chat.id, message.text)
    print(message)


bot.polling(none_stop=True)
