class User:
	def __init__(self, name: str) -> None:
		self.name = name

	@property
	def slug(self) -> str:
		return self.name.lower().replace(' ', '-')
