from typing import Dict

from attrs import define, field
from cattrs.gen import make_dict_unstructure_fn, override
from cattrs.preconf.pyyaml import make_converter

@define
class Cache:

	enabled: bool = field( default=False )

	filesizes: Dict[int, int] = field( factory=dict )

	def filesize( self, item_id: int, filesize: int ):
		if self.enabled:
			self.filesizes[item_id] = filesize

	def cmp_filesize( self, item_id: int, filesize: int ) -> bool:
		return filesize == self.filesizes.get( item_id )

# structuring/unstructuring

conv = make_converter()
hook = make_dict_unstructure_fn( Cache, conv, enabled=override( omit=True ) )
conv.register_unstructure_hook( Cache, hook )

def dumps( cache: Cache ) -> str:
	return conv.dumps( cache )

def loads( data: str ) -> Cache:
	return conv.loads( data, Cache )
