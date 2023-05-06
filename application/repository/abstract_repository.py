from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Protocol, Any

# копируем из буккипера для дальнейшего удобства перемасштабирования


class Model(Protocol):  # pylint: disable=too-few-public-methods
    """
    Модель должна содержать атрибут pk
    """
    pk: int


T = TypeVar('T', bound=Model)


# абстрактный репозиторий - класс, объекты реализаций которого
# в будущем будут отвечать за работу с разными типами моделей
# именно поэтому нужно тип объекта в аргументе
class AbstractRepository(ABC, Generic[T]):
    """
    Абстрактный репозиторий.
    Абстрактные методы:
    add
    get
    get_all
    update
    delete
    """

    @abstractmethod
    def add(self, obj: T) -> int:
        """
        Добавить объект в репозиторий, вернуть id объекта,
        также записать id в атрибут pk.
        """

    @abstractmethod
    def get(self, pk: int) -> T | None:
        """ Получить объект по id """

    @abstractmethod
    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """

    @abstractmethod
    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """

    @abstractmethod
    def delete(self, pk: int) -> None:
        """ Удалить запись """
