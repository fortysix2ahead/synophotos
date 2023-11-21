from logging import getLogger
from os.path import dirname
from typing import Dict, List, Optional, Tuple

from attrs import define, field
from click import get_current_context
from fs.osfs import OSFS

from synophotos import Cache
from synophotos.photos import Album, Item

log = getLogger( __name__ )

@define
class SyncResult:

	fs: OSFS = field( default=None )
	additions: List[Tuple[Item, Album]] = field( factory=list )
	updates: List[Tuple[Item, Album]] = field( factory=list )
	skips: List[Tuple[Item, Album]] = field( factory=list )
	removals: List[str] = field( factory=list )

	def lengths( self ) -> Tuple[int, int, int, int]:
		return len( self.additions ), len( self.updates ), len( self.removals ), len( self.skips )

def prepare_sync_albums( albums: Dict[Album, List[Item]], destination: str, use_cache: bool = False ) -> SyncResult:
	if use_cache:
		cache = get_current_context().obj.cache
		log.info( f'using cache with {len( cache.filesizes )} filesize entries to detect updates' )
	else:
		cache = None

	fs = OSFS( root_path=destination, expand_vars=True, create=True )
	result = SyncResult( fs = fs )

	for album, item_list in albums.items():
		for item in item_list:
			# path = f'/{album.id} - {album.name}/{item.filename}' # don't use album name as it might contain characters which cannot be used in filenames
			if not fs.exists( _item_path( item ) ):
				result.additions.append( ( item, album ) )
			elif cache and not cache.cmp_filesize( item.id, item.filesize ):
				# todo: updates seem (almost) impossible as items do not have a last_modified field
				# work around: remember file sizes and check if there are any changes
				result.updates.append( (item, album ) )
			else:
				result.skips.append( (item, album ) )

	# deduplicate results
	result.additions = list( {i.id: (i, a) for i, a in result.additions}.values() )
	result.updates = list( {i.id: (i, a) for i, a in result.updates}.values() )
	result.skips = list( {i.id: (i, a) for i, a in result.skips}.values() )

	# check for removals
	paths = [ _item_path( r[0] ) for r in result.additions ]
	paths.extend( [ _item_path( r[0] ) for r in result.updates ] )
	paths.extend( [ _item_path( r[0] ) for r in result.skips ] )
	for f in fs.walk.files( filter=[ '*.jpg', '*.jpeg' ] ):
		if f not in paths:
			result.removals.append( f )

	log.info( f'sync result preparation (add/update/remove/skip): {result.lengths()}' )

	return result

def write_item( item: Item, contents: bytes, fs: OSFS ):
	path = _item_path( item )
	fs.makedirs( dirname( path ), recreate=True )
	fs.writebytes( path, contents )
	log.info( f'saved item {item.id} to {fs.getsyspath( path )}, wrote {item.filesize} bytes' )

def remove_item( fs: OSFS, path: str ):
	fs.remove( path )
	log.info( f'removed item from {fs.getsyspath( path )}' )

	if not fs.listdir( dirname( path ) ):
		fs.removedir( dirname( path ) )

def _item_path( item: Item ) -> str:
	# path = f'/{album.id} - {album.name}/{item.filename}' # don't use album name as it might contain characters which cannot be used in filenames
	return f'/{item.folder_id}/{item.filename}'
