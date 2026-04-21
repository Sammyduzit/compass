from dataclasses import dataclass


@dataclass(frozen=True)
class AdapterOutput:
	adapter_name: str
	content: str
