from .service import UserService


def refresh() -> None:
	UserService().load('Grace')
