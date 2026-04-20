from dataclasses import dataclass

@dataclass(frozen=True)
class CouplingPair:
    file_a: str
    file_b: str
    degree: int
