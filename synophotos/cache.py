from typing import Dict

from attrs import define, field

@define
class Cache:

	filesizes: Dict[int, int] = field( factory=dict )
