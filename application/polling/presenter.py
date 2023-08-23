from application.repository.sqlite_repository import SQLiteRepository
from application.models import Meal,Norm
from view import Bot
import config

# создаем бд

# репозиторий в ОП нужен для тестирования, оставим на всякий это здесь
#meal_repo = MemoryRepository()
#norm_repo = MemoryRepository()

meal_repo = SQLiteRepository(Meal)
norm_repo = SQLiteRepository(Norm)

# возможно, их правильнее создавать по команде start

# создаем тг-бота

tele = Bot(config.TOKEN, meal_repo, norm_repo)

# запускаем тг-бота

tele.run()
