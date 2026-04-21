from .models import User
from .service import UserService

def handle(name: str) -> User:
    return UserService().load(name)
