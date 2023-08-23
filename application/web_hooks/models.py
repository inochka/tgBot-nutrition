from datetime import datetime

# нам нужны модели отдельного приема пищи и модели норм питания


class Meal:

    pk: int = 0
    # primary key
    name: str = ""
    # name

    # telegram used id
    user: str

    # calories, lipids, carbohydrates, proteins
    # порядок согласован со строкой формата в классе Bot
    cals: int = 0
    proteins: int = 0
    lipids: int = 0
    carbs: int = 0

    # в перспективе - вводить это на 100 грамм продукта, и далее умножать на массу, поскольку так удобнее

    dt: datetime
    # date and time of meal

    def __init__(self, user, name="", pk=0, dt=datetime.now(), cals=0, lipids=0, carbs=0, proteins=0):
        self.pk = pk
        self.dt = dt
        self.cals = cals
        self.lipids = lipids
        self.carbs = carbs
        self.proteins = proteins
        self.user = user
        self.name = name


class Norm:

    # даты начала и конца периода, в течение которых действует данная норма
    #dt_start: datetime.date
    #dt_end: datetime.date
    pk: int = 0

    # telegram used id
    user: str

    # также у нас будет словарь, ключи в котором - названия параметров
    # а значения - списки из нижнего и верхнего порогов

    #admissible_vals: dict[str, list]

    cals: str
    proteins: str
    lipids: str
    carbs: str

    # нужно переписать и заменить на строки формата мин-мах, так проще всего
    # будет работать с бд

    def __init__(self, user, cals, proteins, lipids, carbs, pk=0):
        self.cals = cals
        self.proteins = proteins
        self. lipids = lipids
        self.carbs = carbs
        self.user = user
        self.pk = pk





