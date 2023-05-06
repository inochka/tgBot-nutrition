from datetime import datetime

# нам нужны модели отдельного приема пищи и модели норм питания


class Meal():

    pk: int = 0
    # primary key
    name: str = ""
    # name

    # calories, lipids, carbohydrates, proteins
    # порядок согласован со строкой формата в классе Bot
    cals: int = 0
    proteins: int = 0
    lipids: int = 0
    carbs: int = 0

    dt: datetime
    # date and time of meal

    def __init__(self, pk = 0, dt=datetime.now(), cals=0, lipids=0, carbs=0, proteins=0):
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
    pk: int = 0

    # также у нас будет словарь, ключи в котором - названия параметров
    # а значения - списки из нижнего и верхнего порогов

    admissible_vals: dict[str, list]

    def __init__(self, dt_start: datetime.date, dt_end: datetime.date, adm_vals: dict[str, list]):
        self.dt_start = dt_start
        self.dt_end = dt_end
        self.admissible_vals = adm_vals


#print(Meal(cals=80))






