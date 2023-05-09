import telebot
import config
from application.repository.abstract_repository import AbstractRepository
from application.models import Meal, Norm
from inspect import get_annotations
from keyboa import Keyboa
import prettytable as pt
from datetime import datetime


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
                "bot_help": "Помощь",
                "meal_add": "Добавить прием пищи",
                "meal_delete": "Удалить прием пищи",
                "meals_show": "Вывести последние 20 приемов пищи",
                "norm_add": "Добавить норму БЖУ",
                "norm_delete": "Удалить норму БЖУ",
                "norms_show": "Удалить норму БЖУ",
                "stats": "Показать статистику",
                "keyboard": "Вывести виртуальную клавиатуру"
                }



    def __init__(self, TOKEN, meal_repo, norm_repo):
        self.token = TOKEN
        # сразу же парсим в хтмл, чтобы было проще
        self.bot = telebot.TeleBot(self.token, parse_mode="HTML")
        self.meal_repo = meal_repo
        self.norm_repo = norm_repo
        self.meal_output_format = ["N0", "Блюдо", "Калории", "Белки", "Жиры", "Углеводы", "Дата(дд-мм-гг)"]
        self.norm_output_format = ["N0", "Калории Min-Max", "Белки Min-Max", "Жиры Min-Max", "Углеводы Min-Max"]

        self.meal_help_string = "<b>Пример ввода приема пищи:</b>\n\n" + " ".join(self.meal_output_format[1:]) +\
                                "\nБиг-мак 200 10 10 10 06-05-2023"
        self.norm_help_string = "<b>Пример ввода нормы БЖУ:</b>\n\n" +"\n".join(self.norm_output_format[1:]) +\
                                "\n\n2000-2500\n120-180\n20-50\n200-300"

        # порядок вывода для блюд

        # заполняем поля
        self.meal_fields = get_annotations(Meal, eval_str=True)
        self.meal_fields.pop('pk')
        self.meal_fields.pop('user')

        self.norm_fields = get_annotations(Norm, eval_str=True)
        self.norm_fields.pop('pk')
        self.norm_fields.pop('user')

           # считаем из файла более длинное текстовое описание

        with open('help.txt', 'r', encoding='utf-8') as f:
            self.general_help_string = f.read()
            #print(self.general_help_string)
        f.close()

        @self.bot.message_handler(commands=["start"])
        # в перспективе можно для каждого юзера сделать свою ветку/таблицу бд
        # тогда нужно создавать/открывать бд по команде старт
        # и удалять по команде енд
        #####     инициализация работы     ###################
        def welcome(message):
            self.bot.send_message(message.chat.id, f"Добро пожаловать, {message.from_user.first_name}!\n" +
                                  "Введи команду /help, если потребуется помощь!\n")
            # виртуальная клавиатура
            make_keyboard(message)


        @self.bot.message_handler(commands=["keyboard"])
        def make_keyboard(message):
            menu = [["Добавить ПП", "Удалить ПП", "Вывести ПП"],
                    ["Добавить норму", "Удалить норму", "Вывести нормы"],
                    ["Помощь", "Статистика"]]
            keyboard = Keyboa(items=menu)
            self.bot.send_message(chat_id=message.chat.id, text="Выберите нужное действие", reply_markup=keyboard())
            self.bot.send_message(chat_id=message.chat.id, text="Здесь ПП - прием пищи, а норма - "
                                                                "суточная норма калорий и БЖУ")

        # обработчик нажатий на клавиатуру
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_keyboard(call):
            actions = {"Добавить ПП": meal_add_request_data, "Удалить ПП": meal_delete_request_data,
                       "Вывести ПП": meals_show, "Добавить норму": norm_add_request_data,
                       "Удалить норму": norm_delete_request_data, "Вывести нормы": norms_show,
                       "Помощь": bot_help, "Статистика": stats}
            # была охуевшая ошибка из-за того, что команда help дублировалась аналогичной комадной бота
            if call.data in actions.keys():
                # вызываем функции по имени в зависимости от введенной команды
                actions[call.data](call.message)

        @self.bot.message_handler(commands=["bot_help"])
        def bot_help(message):
            msg = self.general_help_string + "\n\n" + "<b> Список команд </b>\n"
            for key in self.commands.keys():
                msg += f"/{key}: {self.commands[key]}\n"

            msg += "\n\n" + self.meal_help_string + "\n\n" + self.norm_help_string

            self.bot.send_message(message.chat.id, msg)


        #####     данные о приемах пищи     ###################


        @self.bot.message_handler(commands=["meal_add"])
        def meal_add_request_data(message):
            self.bot.send_message(message.chat.id, "Введите данные о приеме пищи в формате:\n" +
                                  " ".join(self.meal_output_format[1:]))
            # номер сами не вводим, он генерится автоматически
            self.bot.register_next_step_handler(message, meal_add)
            # в перспективе сделать ввод данных опциональным, с предустановленным сегодняшним днем

        def meal_add(message):
            try:
                meal_data = message.text.split(" ")
                #print(meal_data)
                # руками добавляем id юзера, добавившего запись
                new_meal = Meal(user=str(message.from_user.id))
                # !!! добавить проверку на ошибки при вводе сюда!!

                i = 0

                if len(meal_data) != len(self.meal_fields):
                    raise (ValueError, "Не все позиции заполнены!")

                for field in self.meal_fields.keys():
                    setattr(new_meal, field, meal_data[i])
                    i += 1

                meal_repo.add(new_meal)
                self.bot.send_message(message.chat.id, "Вы успешно ввели данные о приеме пищи")
            except Exception as e:
                print(e)
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
            data = meal_repo.get_all({"user": str(message.from_user.id)})
            # сортируем по дате: от более нового к более старому
            data.sort(key=lambda meal: datetime.strptime(meal.dt, "%d-%m-%Y"), reverse=True)



            if not data:
                self.bot.send_message(message.chat.id, "Извините, записей о вашем питании не найдено.")
            else:
                # зададим также максимальное количество выводимых записей
                # в дальнейшем по дате мб можно будет настроить выборку, но пока забьем
                bound = 20
                i = 0
                output_data = []

                dt = data[0].dt

                for row in data:
                    # если дата поменялась, делаем отступ в одну строчку в таблице
                    if row.dt != dt:
                        output_data.append([" "] * (len(list(self.meal_fields.keys())) + 1))
                    dt = row.dt

                    if i >= bound:
                        break

                    i += 1
                    output_data.append([str(row.pk)] + [getattr(row, field) for field in self.meal_fields.keys()])

                self.send_table(message, self.meal_output_format, output_data)

        #####     данные о нормах калоража     ###################

        @self.bot.message_handler(commands=["norm_add"])
        def norm_add_request_data(message):
            self.bot.send_message(message.chat.id, "Введите данные о суточной норме БЖУ в формате:\n\n" +
                                  "\n".join(self.norm_output_format[1:]))
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
                    admissible_vals[field] = norm_data[i]
                    #.split("-")
                    i += 1
                # вспоминаем, что нужно добавить также id пользователя
                norm_repo.add(Norm(user=str(message.from_user.id), **admissible_vals))
                self.bot.send_message(message.chat.id, "Вы успешно ввели данные о норме БЖУ")
            except:
                self.bot.send_message(message.chat.id, "При вводе данных о норме БЖУ возникла ошибка!")

        @self.bot.message_handler(commands=["norms_show"])
        def norms_show(message):
            data = norm_repo.get_all({"user": str(message.from_user.id)})

            if not data:
                self.bot.send_message(message.chat.id, "Извините, записей о ваших нормах БЖУ не найдено.")
            else:
                # зададим также максимальное количество выводимых записей
                bound = 20
                i = 0
                output_data = []
                for row in data:
                    if i >= bound:
                        break
                    i += 1
                    #output_data.append([str(row.pk)] +
                    #                   [str(field[0]) + " - " + str(field[1]) for field in row.admissible_vals.values()])

                    output_data.append([str(row.pk)] + [getattr(row, field) for field in self.norm_fields])

                self.send_table(message, self.norm_output_format, output_data)

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

                self.norm_repo.delete(norm_pk)
                # нужно дописать
                self.bot.send_message(message.chat.id, "Вы успешно удалили данные о норме БЖУ")
            except:
                self.bot.send_message(message.chat.id, "При удалении данных о норме БЖУ возникла ошибка!")

        @self.bot.message_handler(commands=["stats"])
        def stats(message):
            pass

        @self.bot.message_handler(content_types=["text"])
        def not_recognised(message):
            self.bot.send_message(message.chat.id, "Извините, команда не распознана.")

    def send_table(self, message, headers, data):
        # headers - list of strings-names
        table = pt.PrettyTable(headers)
        for header in headers:
            table.align[header] = "c"

        for row in data:
            # row is a list of strings
            table.add_row(row)

        self.bot.send_message(message.chat.id, f'<pre>{table}</pre>')

    def run(self):
        self.bot.polling(none_stop=True)
