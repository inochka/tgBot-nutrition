from datetime import datetime

# нам нужны модели отдельного приема пищи и модели норм питания


class Meal():
    dt: datetime
    # date and time of meal
    pk: int = 0
    # primary key
    name: str = 0
    # name

    # calories, lipids, carbohydrates, proteins
    cals: int = 0
    lipids: int = 0
    carbs: int = 0
    proteins: int = 0

    def __init__(self, pk, dt=datetime.now(), cals=0, lipids=0, carbs=0, proteins=0):
        self.pk = pk
        self.dt = dt
        self.cals = cals
        self.lipids = lipids
        self.carbs = carbs
        self.proteins = proteins


class Norm():

    # даты начала и конца периода, в течение которых действует данная норма
    dt_start: datetime.date
    dt_end: datetime.date

    # также у нас будет словарь, ключи в котором - названия параметров
    # а значения - списки из нижнего и верхнего порогов

    admissible_vals: dict[str, list]

    def __init__(self, dt_start: datetime.date, dt_end: datetime.date, adm_vals: dict[str, list]):
        self.dt_start = dt_start
        self.dt_end = dt_end
        self.admissible_vals = adm_vals


print(Meal(pk=1, cals = 80))






