from .models import User


class UserRepository:
	def get(self, name: str) -> User:
		return User(name)
