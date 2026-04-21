from collections.abc import Callable

from .models import User
from .repository import UserRepository


def audited(func: Callable[[object, str], User]) -> Callable[[object, str], User]:
	return func


class UserService:
	def __init__(self) -> None:
		self.repository = UserRepository()

	@staticmethod
	def normalize(name: str) -> str:
		return name.strip()

	@audited
	def load(self, name: str) -> User:
		try:
			user = self.repository.get(self.normalize(name))
			return user
		except ValueError as exc:
			raise RuntimeError('could not load user') from exc
