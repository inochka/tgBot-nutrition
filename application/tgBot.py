import telebot
import config
from application.repository.abstract_repository import AbstractRepository
from application.models import Meal,Norm
from inspect import get_annotations, getmembers


"""
import telepot
token = '6226679318:AAHypKT7bQFLgkwpK7gfcZ4W0WI1TvgzaYc'
TelegramBot = telebot.Bot(token)
print(TelegramBot.getMe())
print(TelegramBot.getUpdates()[0])
"""


class Bot:
    TOKEN: str
    bot: telebot.TeleBot
    meal_repo: AbstractRepository
    norms_repo: AbstractRepository

    meal_fields: dict
    norm_fields: dict

    # список допустимых команд
    commands = {"start" : "Начать взаимодействие",
                "end" : "Закончить взаимодействие",
                "help": "Помощь",
                "add_meal": "Добавить прием пищи",
                "delete_meal": "Удалить прием пищи",
                "edit_meal": "Редактировать прием пищи",
                "show_meals": "Вывести последние 10 приемов пищи",
                "add_norm": "Добавить норму БЖУ",
                "delete_norm": "Удалить норму БЖУ",
                "stats": "Показать статистику"
                }

    def __init__(self, TOKEN, meal_repo, norm_repo):
        self.token = TOKEN
        self.bot = telebot.TeleBot(self.token)
        self.meal_repo = meal_repo
        self.norm_repo = norm_repo
        self.meal_ouptut_format = "Блюдо Калории Белки Жиры Углеводы Дата(мм-дд-гг)"
        # порядок вывода для блюд

        # заполняем поля
        self.meal_fields = get_annotations(Meal, eval_str=True)
        self.meal_fields.pop('pk')

        self.norm_fields = get_annotations(Norm, eval_str=True)
        self.norm_fields.pop('pk')


        @self.bot.message_handler(commands=["start"])
        def welcome(message):
            self.bot.send_message(message.chat.id, f"Добро пожаловать, {message.from_user.first_name}!")
            self.bot.send_message(message.chat.id, "Введи команду /help, если потребуется помощь!\n")

        @self.bot.message_handler(commands=["help"])
        def help(message):
            self.bot.send_message(message.chat.id, "Смотри, что я умею:")
            msg = ""
            for key in self.commands.keys():
                msg += f"/{key}: {self.commands[key]}\n"

            self.bot.send_message(message.chat.id, msg)

        @self.bot.message_handler(commands=["add_meal"])
        def meal_request_data(message):
            self.bot.send_message(message.chat.id, "Введите данные о приеме пищи в формате:\n"+
                                                  self.meal_ouptut_format)
            self.bot.register_next_step_handler(message, meal_create)
            # в перспективе сделать ввод данных опциональным, с предустановленным сегодняшним днем

        def meal_create(message):
            try:
                meal_data = message.text.split(" ")
                new_meal = Meal()
                # !!! добавить проверку на ошибки при вводе сюда!!

                i = 0
                #print(self.meal_fields.keys())
                for field in self.meal_fields.keys():
                    setattr(new_meal, field, meal_data[i])
                    #print(field + getattr(new_meal, field))
                    i += 1

                #print(new_meal)
                meal_repo.add(new_meal)
                self.bot.send_message(message.chat.id, "Вы успешно ввели данные о приеме пищи")
                #print(meal_repo.get_all())
            except:
                self.bot.send_message(message.chat.id, "При вводе данных о приеме пищи возникла ошибка!")

        @self.bot.message_handler(commands=["show_meals"])
        def show_meals(message):
            #нужно будет здесь побольше функционала и выборов добавить
            data = meal_repo.get_all()
            #print(meal_repo)
            output = ""

            if not data:
                self.bot.send_message(message.chat.id, "Извините, записей о вашем питании не найдено.")
            else:
                self.bot.send_message(message.chat.id, self.meal_ouptut_format)
                for row in data:
                    output += " ".join([getattr(row, field) for field in self.meal_fields.keys()]) + "\n"

                self.bot.send_message(message.chat.id, output)

        @self.bot.message_handler(content_types=["text"])
        def answer(message):
            self.bot.send_message(message.chat.id, message.text)
            #print(message)

    def run(self):
        self.bot.polling(none_stop=True)



"""
    bot = telebot.TeleBot(config.TOKEN)


if __name__ == '__main__':
    Tele = Telegram()
    Tele.run()
"""
