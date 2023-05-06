from application.repository.memory_repository import MemoryRepository

from application.models import Meal,Norm

rep = MemoryRepository()
rep.add(Meal(cals = 80))

print(rep)
