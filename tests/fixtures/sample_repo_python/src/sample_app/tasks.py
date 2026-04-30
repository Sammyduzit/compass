from .service import UserService

def refresh() -> None:
    user = UserService().load('Grace')
    print(user.slug)
