import telebot
import config
from application.repository.abstract_repository import AbstractRepository
from application.models import Meal, Norm
from inspect import get_annotations
from keyboa import Keyboa

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
    commands = {"start": "Начать взаимодействие",
                #"end": "Закончить взаимодействие",
                "help": "Помощь",
                "meal_add": "Добавить прием пищи",
                "meal_delete": "Удалить прием пищи",
                #"meal_edit": "Редактировать прием пищи",
                "meals_show": "Вывести последние 20 приемов пищи",
                "norm_add": "Добавить норму БЖУ",
                "norm_delete": "Удалить норму БЖУ",
                "norms_show": "Удалить норму БЖУ",
                "stats": "Показать статистику",
                "keyboard": "Вывести виртуальную клавиатуру"
                }

    def __init__(self, TOKEN, meal_repo, norm_repo):
        self.token = TOKEN
        self.bot = telebot.TeleBot(self.token)
        self.meal_repo = meal_repo
        self.norm_repo = norm_repo
        self.meal_ouptut_format = "Блюдо Калории Белки Жиры Углеводы Дата(мм-дд-гг)"
        self.norm_ouptut_format = "КалорииMin-КалорииMax \nБелкиMin-БелкиMax\nЖирыMin-ЖирыMax\nУглеводыMin-УглеводыMax"
        # порядок вывода для блюд

        # заполняем поля
        self.meal_fields = get_annotations(Meal, eval_str=True)
        self.meal_fields.pop('pk')

        self.norm_fields = get_annotations(Norm, eval_str=True)
        #self.norm_fields.pop('pk')

        @self.bot.message_handler(commands=["start"])
        # в перспективе можно для каждого юзера сделать свою ветку/таблицу бд
        # тогда нужно создавать/открывать бд по команде старт
        # и удалять по команде енд

        #####     инициализация работы     ###################
        def welcome(message):
            self.bot.send_message(message.chat.id, f"Добро пожаловать, {message.from_user.first_name}!")
            self.bot.send_message(message.chat.id, "Введи команду /help, если потребуется помощь!\n")
            # виртуальная клавиатура
            make_keyboard(message)


        @self.bot.message_handler(commands=["keyboard"])
        def make_keyboard(message):
            menu = [["Добавить ПП", "Удалить ПП", "Вывести ПП"],
                    ["Добавить норму", "Удалить норму", "Вывести нормы"],
                    ["Помощь", "Статистика"]]
            keyboard = Keyboa(items=menu)
            self.bot.send_message(chat_id=message.chat.id, text="Выберите нужное действие", reply_markup=keyboard())
            self.bot.send_message(chat_id=message.chat.id, text="Здесь ПП - прием пищи, а норма - суточная норма калорий и БЖУ")

        # обработчик нажатий на клавиатуру
        @self.bot.callback_query_handler(func=lambda call: True)
        def send_text(call):
            actions = {"Добавить ПП": meal_add_request_data, "Удалить ПП": meal_delete_request_data,
                       "Вывести ПП": meals_show, "Добавить норму": norm_add_request_data,
                       "Удалить норму": norm_delete_request_data, "Вывести нормы": norms_show,
                       "Помощь": help, "Статистика": statistics}
            if call.data in actions.keys():
                actions[call.data](call.message)



        @self.bot.message_handler(commands=["help"])
        def help(message):
            self.bot.send_message(message.chat.id, "Смотри, что я умею:")
            msg = ""
            for key in self.commands.keys():
                msg += f"/{key}: {self.commands[key]}\n"

            self.bot.send_message(message.chat.id, msg)


        #####     данные о приемах пищи     ###################


        @self.bot.message_handler(commands=["meal_add"])
        def meal_add_request_data(message):
            self.bot.send_message(message.chat.id, "Введите данные о приеме пищи в формате:\n" +
                                  self.meal_ouptut_format)
            self.bot.register_next_step_handler(message, meal_add)
            # в перспективе сделать ввод данных опциональным, с предустановленным сегодняшним днем

        def meal_add(message):
            try:
                meal_data = message.text.split(" ")
                print(meal_data)
                new_meal = Meal()
                # !!! добавить проверку на ошибки при вводе сюда!!

                i = 0

                if len(meal_data) != len(self.meal_fields):
                    raise (ValueError, "Не все позиции заполнены!")

                for field in self.meal_fields.keys():
                    setattr(new_meal, field, meal_data[i])
                    i += 1

                meal_repo.add(new_meal)
                self.bot.send_message(message.chat.id, "Вы успешно ввели данные о приеме пищи")
            except:
                self.bot.send_message(message.chat.id, "При вводе данных о приеме пищи возникла ошибка!")

        @self.bot.message_handler(commands=["meal_delete"])
        def meal_delete_request_data(message):
            self.bot.send_message(message.chat.id, "Введите порядковый номер записи, которую вы хотите удалить:\n")
            self.bot.register_next_step_handler(message, meal_delete)

        def meal_delete(message):
             try:
                meal_pk = int(message.text)

                if meal_pk < 0:
                    raise (ValueError, "Введите корректную информацию!")

                self.meal_repo.delete(meal_pk)
                # нужно дописать
                self.bot.send_message(message.chat.id, "Вы успешно удалили данные о приеме пищи")
             except:
                self.bot.send_message(message.chat.id, "При удалении данных о приеме пищи возникла ошибка!")


        @self.bot.message_handler(commands=["meals_show"])
        def meals_show(message):
            # нужно будет здесь побольше функционала и выборов добавить
            data = meal_repo.get_all()
            output = ""

            if not data:
                self.bot.send_message(message.chat.id, "Извините, записей о вашем питании не найдено.")
            else:
                # зададим также максимальное количество выводимых записей
                # в дальнейшем по дате мб можно будет настроить выборку, но пока забьем
                bound = 20
                i = 0
                self.bot.send_message(message.chat.id, self.meal_ouptut_format)
                date = ""
                for row in data:
                    if i >= bound:
                        break
                    i += 1

                    output += str(row.pk) + " " + " ".join([getattr(row, field) for field in self.meal_fields.keys()]) + "\n"

                    date = row.dt

                self.bot.send_message(message.chat.id, output)

        #####     данные о нормах калоража     ###################

        @self.bot.message_handler(commands=["norm_add"])
        def norm_add_request_data(message):
            self.bot.send_message(message.chat.id, "Введите данные о суточной норме БЖУ в формате:\n" +
                                  self.norm_ouptut_format)
            self.bot.register_next_step_handler(message, norm_add)
            # в перспективе сделать ввод данных опциональным, с предустановленным сегодняшним днем

        def norm_add(message):
            try:
                norm_data = message.text.split("\n")
                admissible_vals = {}
                i = 0
                for field in self.meal_fields.keys():
                    if field == "dt" or field == "name":
                        continue
                    # нужно добавить проверки на корректность данных и проч
                    admissible_vals[field] = norm_data[i].split("-")
                    i += 1
                norm_repo.add(Norm(admissible_vals))
                self.bot.send_message(message.chat.id, "Вы успешно ввели данные о норме БЖУ")
            except:
                self.bot.send_message(message.chat.id, "При вводе данных о норме БЖУ возникла ошибка!")

        @self.bot.message_handler(commands=["norms_show"])
        def norms_show(message):
            data = norm_repo.get_all()
            output = ""

            if not data:
                self.bot.send_message(message.chat.id, "Извините, записей о ваших нормах БЖУ не найдено.")
            else:
                # зададим также максимальное количество выводимых записей
                bound = 20
                i = 0
                # заменяем переносы строки на табуляции для удобства
                self.bot.send_message(message.chat.id, "Калории\tБелки\tЖиры\tУглеводы")
                date = ""
                for row in data:
                    if i >= bound:
                        break
                    i += 1
                    vals = [str(field[0]) + " - " + str(field[1]) for field in row.admissible_vals.values()]
                    #print(vals)

                    output += str(row.pk) + "\t" + "\t".join(vals) + "\n"

                self.bot.send_message(message.chat.id, output)

        @self.bot.message_handler(commands=["norm_delete"])
        def norm_delete_request_data(message):
            self.bot.send_message(message.chat.id, "Введите порядковый номер записи, которую вы хотите удалить:\n")
            self.bot.register_next_step_handler(message, norm_delete)

        def norm_delete(message):
            try:
                # добавить бы сюда вывод того, что мы удаляем
                norm_pk = int(message.text)

                if norm_pk < 0:
                    raise (ValueError, "Введите корректную информацию!")

                #deleting_data = meal_repo.get(norm_pk)
                self.norm_repo.delete(norm_pk)
                # нужно дописать
                self.bot.send_message(message.chat.id, "Вы успешно удалили данные о норме БЖУ")
            except:
                self.bot.send_message(message.chat.id, "При удалении данных о норме БЖУ возникла ошибка!")

        @self.bot.message_handler(commands=["statistics"])
        def statistics(message):
            pass
        @self.bot.message_handler(content_types=["text"])
        def answer(message):
            self.bot.send_message(message.chat.id, message.text)

    def run(self):
        self.bot.polling(none_stop=True)