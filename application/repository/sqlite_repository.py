from inspect import get_annotations
import sqlite3
from application.repository.abstract_repository import AbstractRepository, T
from application.models import Meal
from application.models import Norm
from typing import Any
import application.config as config


class SQLiteRepository(AbstractRepository[T]):

    db_file: str
    cls: type
    table_name: str
    fields: dict

# нужно создать бд и добавить путь к ней
    def __init__(self, cls: type, db_file: str = config.DB_PATH) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        # имя таблицы должно быть ловеркейсом от имени класса
        self.fields = get_annotations(cls, eval_str=True)
        # и поля должны быть в точности такие же, как и аттрибуты
        self.fields.pop('pk')
        self.cls = cls

    def create_db(self):
        """метод, который будет создавать бд при первой инициализации программы"""

    # метод, который преобразовывает выхлоп sqlite в словарь
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def add(self, obj: T) -> int:
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        # all attrs have to be strings or numbers
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            #cur.execute("PRAGMA foreign_keys = ON")
            cur.execute(f'INSERT INTO {self.table_name} ({names}) VALUES ({p})', values)
            obj.pk = cur.lastrowid

        con.close()
        return obj.pk

    """ Получить объект по id """
    #видимо, получаем объект заданного класса
    def get(self, pk: int) -> T | None:
        # открываем соединение и работаем
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.row_factory = self.dict_factory
            cur.execute("SELECT * FROM " + self.table_name +
                        " WHERE pk =?;", (pk,))
            rows = cur.fetchall()
            #print(rows)

        con.close()

        # обрабатываем случай, когда записи с таким ключом не нашлось
        if not rows:
            return None

        return self.cls(** rows[0])

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.row_factory = self.dict_factory

            # создадим строку условий
            values = []
            cond = ""
            # по умолчанию where - это  None
            if where is not None:
                cond = " WHERE"
                i = 0
                for field in (list(self.fields.keys()) + ["pk"]):
                    #print(field)
                    if where.get(field) is not None:
                        if i != 0:
                            cond += " AND "
                            i += 1

                        cond += "(" + field + " = ?)"
                        values.append(where.get(field))


            # print("SELECT * FROM " + self.table_name + cond + ";")
            # print(values)
            cur.execute("SELECT * FROM " + self.table_name + cond + ";", values)
            rows = cur.fetchall()
            # print(rows)

        con.close()

        if not rows:
            return []
        # возвращаем список объектов
        return [self.cls(** row) for row in rows]

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """

        # проверяяем, чтобы ключ присутствовал
        if getattr(obj, "pk") is None:
            raise ValueError("CANNOT UPDATE A RECORD! RECEIVED OBJECT DOESN'T HAVE PRIMARY KEY!\n")

        # проверяем, чтобы ключ был неотрицательным целым числом
        if int(getattr(obj, "pk")) < 0:
            raise KeyError("CANNOT UPDATE A RECORD! RECEIVED OBJECT HAS INVALID PRIMARY KEY!\n")

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.row_factory = self.dict_factory

            # создаем названия полей, pk и так нет по построению
            names = ' = ?, '.join(self.fields.keys()) + " = ?"
            # создаем ? для дальнейшей вставки, pk и так нет по построению
            p = ', '.join("?" * len(self.fields))

            # print(names)

            values = [getattr(obj, x) for x in self.fields]
            # print("UPDATE " + self.table_name + " SET " + names + " WHERE pk = ? ;")
            # print(values + [str(obj.pk)])

            cur.execute("UPDATE " + self.table_name + " SET " + names + " WHERE pk = ? ;", values + [str(obj.pk)])

        con.close()

    def delete(self, pk: int) -> None:

        # проверяем, чтобы ключ был неотрицательным целым числом
        if int(pk) < 0:
            raise KeyError("CANNOT DELETE A RECORD! RECEIVED OBJECT HAS INVALID PRIMARY KEY!\n")

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.row_factory = self.dict_factory

            cur.execute("DELETE FROM " + self.table_name + " WHERE pk = ? ;", (pk,))
            #print("deleted:" + str(cur.rowcount))

            # проверяем, что мы не пытаемся удалить несуществующую запись
            if cur.rowcount == 0:
                raise KeyError("CANNOT DELETE A NON EXISTING RECORD!\n")

        con.close()
