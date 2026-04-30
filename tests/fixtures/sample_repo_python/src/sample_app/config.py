from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    retries: int = 3
