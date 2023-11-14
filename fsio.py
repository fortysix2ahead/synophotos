from logging import getLogger
from os.path import dirname
from typing import Dict, List, Tuple

from attrs import define, field
from fs.osfs import OSFS

from synophotos.photos import Album, Item

log = getLogger( __name__ )

@define
class SyncResult:

	fs: OSFS = field( default=None )
	additions: List[Tuple[Item, Album, str]] = field( factory=list )
	updates: List[Tuple[Item, Album, str]] = field( factory=list )
	skips: List[Tuple[Item, Album, str]] = field( factory=list )
	removals: List[str] = field( factory=list )

def prepare_sync_albums( albums: Dict[Album, List[Item]], destination: str ) -> SyncResult:
	fs = OSFS( root_path=destination, expand_vars=True, create=True )
	result = SyncResult( fs = fs )

	for album, item_list in albums.items():
		for item in item_list:
			path = f'/{album.id} - {album.name}/{item.filename}'
			if not fs.exists( path ):
				result.additions.append( ( item, album, path ) )
			elif False:
				result.updates.append( (item, album, path) ) # todo: updates seem impossible as items do not have a last_modified field
			else:
				result.skips.append( (item, album, path) )

	# check for removals
	added, skipped = [ r[2] for r in result.additions ], [ r[2] for r in result.skips ]
	for f in fs.walk.files( filter=[ '*.jpg', '*.jpeg' ] ):
		if f not in added and f not in skipped:
			result.removals.append( f )

	return result

def write_item( item: Item, contents: bytes, fs: OSFS, path: str ):
	fs.makedirs( dirname( path ), recreate=True )
	fs.writebytes( path, contents )
	log.info( f'saved item {item.id} to {fs.getsyspath( path )}, wrote {item.filesize} bytes' )

def remove_item( fs: OSFS, path: str ):
	fs.remove( path )
	log.info( f'removed item from {fs.getsyspath( path )}' )

	if not fs.listdir( dirname( path ) ):
		fs.removedir( dirname( path ) )
