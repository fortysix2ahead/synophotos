
from typing import Dict

def lower_keys( d: Dict ) -> Dict:
	for k, v in d.copy().items():
		d.pop( k )
		d[k.lower()] = lower_keys( v ) if isinstance( v, dict ) else v
	return d
