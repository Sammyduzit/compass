from sample_app.service import UserService


def test_normalize() -> None:
	assert UserService.normalize(' Ada ') == 'Ada'
