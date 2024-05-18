from typing import Dict, Optional

from attrs import define, field
from cattrs.gen import make_dict_unstructure_fn, override
from cattrs.preconf.pyyaml import make_converter
from dynaconf import Dynaconf

@define
class Cache:

	enabled: bool = field( default=False )
	filesizes: Dict[int, int] = field( factory=dict )

	source: Optional[Dynaconf] = field( kw_only=True )

	def __attrs_post_init__( self ):
		if self.source:
			self.filesizes = self.source.as_dict().get( 'FILESIZES' )

	def cmp_filesize( self, item_id: int, filesize: int ) -> bool:
		return filesize == self.filesizes.get( item_id ) if self.enabled else False

# structuring/unstructuring

conv = make_converter()
hook = make_dict_unstructure_fn( Cache, conv, enabled=override( omit=True ), source=override( omit=True ) )
conv.register_unstructure_hook( Cache, hook )

def dumps( cache: Cache ) -> str:
	return conv.dumps( cache )

def loads( data: str ) -> Cache:
	return conv.loads( data, Cache )

# helper

def _cap_dict_keys( d ) -> Dict:
	for k, v in d.copy().items():
		d.pop( k )
		d[k.lower()] = _cap_dict_keys( v ) if isinstance( v, dict ) else v
	return d
