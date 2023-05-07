from application.repository.abstract_repository import AbstractRepository
from application.repository.memory_repository import MemoryRepository
from application.models import Meal,Norm
from tgBot import Bot
import config

# создаем бд

meal_repo = MemoryRepository()
norm_repo = MemoryRepository()
# возможно, их правильнее создавать по команде start

# создаем тг-бота

tele = Bot(config.TOKEN, meal_repo, norm_repo)

# запускаем тг-бота

tele.run()
