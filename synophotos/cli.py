from logging import getLogger
from os.path import dirname
from sys import exit as sysexit
from typing import List, cast, Optional

from click import argument, Context, group, option, pass_context, pass_obj
from fs.osfs import OSFS
from more_itertools import flatten
from yaml import safe_dump

from synophotos import __version__
from synophotos import ApplicationContext
from synophotos.photos import Album, Item, SynoPhotos, ThumbnailSize
from synophotos.ui import obj_table, pprint as pp, print_error, print_obj, print_obj_table, table_for

log = getLogger( __name__ )

synophotos: Optional[SynoPhotos] = None  # global variable for functions below

@group
@option( '-d', '--debug', is_flag=True, required=False, default=False, help='outputs debug information (implies --verbose)' )
@option( '-v', '--verbose', is_flag=True, required=False, default=False, help='outputs verbose log information' )
@pass_context
def cli( ctx: Context, debug: bool, verbose: bool ):
	ctx.obj = ApplicationContext( verbose=verbose, debug=debug )

	if ctx.obj.config.active_profile:
		# create (global) service (to ease login) and add to context
		global synophotos
		synophotos = SynoPhotos( url=ctx.obj.url, account=ctx.obj.account, password=ctx.obj.password, session=ctx.obj.session )
		ctx.obj.service = synophotos

		# attempt to log in
		if not synophotos.login( ctx.obj ):
			#ctx.obj.console.print( f'error logging in code={syno_session.error_code}, msg={syno_session.error_msg}' )
			print_error( 'failed to log in' )
			sysexit( -1 )

@cli.command( help='initializes the application' )
@pass_obj
def init( ctx: ApplicationContext ):
	from synophotos import CFG_FS as fs, CONFIG_FILE, DEFAULT_CONFIG
	if not fs.exists( CONFIG_FILE ):
		fs.writetext( CONFIG_FILE, safe_dump( DEFAULT_CONFIG ) )
		config_path = fs.getsyspath( f'{CONFIG_FILE}' )
		pp( f'Sample configuration has been created in \"{config_path}\"' )
		pp( f'[bold]Important:[/bold] edit this file immediately as any subsequent commands will fail as synophotos will try to contact a non-existing server' )
	else:
		log.info( f'Skipping initialization as configuration file already exist' )

# create

@cli.command( help='creates albums' )
@option( '-f', '--folder', required=False, default=None, help='name of a folder used to populate album', type=str )
@option( '-fid', '--folder-id', required=False, default=None, help='id of a folder used to populate album', type=int )
@option( '-s', '--share', required=False, help='share album with users or groups', type=int )
@argument( 'name', nargs=1, required=True )
@pass_obj
def create( ctx: ApplicationContext,  name: str, folder: str, folder_id: int, share: int = None ):
	if folder:
		if len( folders := synophotos.folders( folder ) ) == 1:
			folder = folders[0]
			log.debug( f'using folder [dark_orange]{folder.name}[/dark_orange] with id {folder.id} to populate album' )

		else:
			print_error( f'a folder for "{name}" does either not exist or multiple folders match: use either an id or provide an unbiguous folder name' )
			return

	elif folder_id:
		folder = synophotos.folder( int( folder ) )

	album = synophotos.create_album( name )
	log.info( f'created album [dark_orange]{album.name}[/dark_orange] with id {album.id}' )

	if folder:
		items = synophotos.list_items( folder.id, recursive=False )
		synophotos.add_album_items( album, items )
		log.info( f'added {len( items )} from [dark_orange]{folder.name}[/dark_orange] to album [dark_orange]{album.name}[/dark_orange]' )

	if share:
		raise NotImplementedError

	pp( album.id )

# count ... not sure if this is useful

@cli.command( 'count', help='counts items' )
@option( '-a', '--albums', required=False, is_flag=True, default=False, help='counts the number of albums', type=bool )
@option( '-f', '--folders', required=False, is_flag=True, default=False, help='counts the number of folders', type=bool )
@option( '-i', '--items', required=False, is_flag=True, default=False, help='counts the number of items', type=bool )
@argument( 'parent_id', nargs=1, required=False, default=0, type=int )
@pass_obj
def count( ctx: ApplicationContext, albums: bool, folders: bool, items: bool, parent_id=0 ):
	if albums:
		pp( synophotos.count_albums() )
	elif folders:
		pp( synophotos.count_folders( parent_id ) )
	elif items:
		if albums:
			pp( synophotos.count_items( album_id=parent_id ) )
		else:
			pp( synophotos.count_items( folder_id=parent_id ) )
	else:
		print_error( 'provide one of the mandatory options -a, -f, -i or use --help to learn more' )

# list

@cli.command( help='lists existing albums and their ids' )
@option( '-s', '--shared', required=False, is_flag=True, default=False, help='include shared elements' )
@argument( 'name', nargs=1, required=False, type=str )
@pass_obj
def albums( ctx: ApplicationContext, name: str, shared: bool ):
		print_obj( synophotos.list_albums( name, shared ) )

@cli.command( help='lists existing folders and their ids' )
@option( '-p', '--parent_id', required=False, default=None, help='id of the parent', type=int )
@option( '-r', '--recursive', required=False, is_flag=True, default=False, help='include all folders recursively', type=bool )
@argument( 'name', nargs=1, required=False, type=str )
@pass_obj
def folders( ctx: ApplicationContext, name: str, parent_id: int, recursive: bool ):
		print_obj( synophotos.list_folders( parent_id, name, recursive ) )

@cli.command( help='lists items' )
@option( '-a', '--album', required=False, default=None, help='id of the parent album', type=int )
@option( '-f', '--folder', required=False, default=None, help='id of the parent folder', type=int )
@option( '-r', '--recursive', required=False, is_flag=True, default=False, help='include all folders recursively', type=bool )
@argument( 'name', nargs=1, required=False, type=str )
@pass_obj
def items( ctx: ApplicationContext, album: int, folder: int, recursive: bool, name: str = None ):
	if recursive:
		pp( '[red]fetching items without paging and/or recursively, this might take a while ...[/red]' )

	if album and folder:
		print_error( '-a and -f cannot be used together, specify only one option' )
		return

	if not album and not folder:
		folder = synophotos.root_folder()

	print_obj( synophotos.list_items( album_id=album, folder_id=folder, recursive=recursive, name=name ) )

@cli.command( help='lists existing groups and their ids' )
@pass_obj
def groups( ctx: ApplicationContext ):
		print_obj( synophotos.list_groups() )

@cli.command( help='lists existing users and their ids' )
@pass_obj
def users( ctx: ApplicationContext ):
		print_obj( synophotos.list_users() )

@cli.command( help='gets the id of the root folder' )
@pass_obj
def root( ctx: ApplicationContext ):
	pp( _ws( ctx ).root_folder().id )

# sharing

@cli.command( help='shares an album' )
@option( '-id', '--album-id', required=False, is_flag=False, default=None, help='id of the album to share, if provided name will be ignored', type=int )
@option( '-r', '--role', required=False, default='view', help='permission role, can be "view", "download" or "upload"' )
@option( '-p', '--public', required=False, is_flag=True, default=False, help='shares the album publicly' )
@option( '-g', '--group', required=False, help='group to share with' )
@option( '-gid', '--group-id', required=False, help='id of a group to share with' )
@option( '-u', '--user', required=False, help='user to share with' )
@option( '-uid', '--user-id', required=False, help='id of a user to share with´' )
@argument( 'name', nargs=1, required=False, type=str )
@pass_obj
def share( ctx: ApplicationContext, name: str, album_id: int, role: str, public: bool, user: str, user_id: int, group: str, group_id: int ):
	if name and not album_id:
		album_ids = [ a.id for a in synophotos.albums( name ) ]
	else:
		album_ids = [ album_id ]

	if group and not group_id:
		group_id = synophotos.id_for_group( group )
	if user and not user_id:
		user_id = synophotos.id_for_user( user )

	log.debug( f'attempting to share albums {album_ids} with user {user_id} and/or group {group_id}' )

	for id in album_ids:
		pp( synophotos.share_album( id, role, public, user_id, group_id ) )

@cli.command( help='unshares an album' )
@option( '-id', '--album-id', required=False, is_flag=False, default=None, help='id of the album to unshare, if provided, name will be ignored', type=int )
@argument( 'name', nargs=1, required=False, type=str )
@pass_obj
def unshare( ctx: ApplicationContext, name: str, album_id: int ):
	album_ids = [ album_id ] if album_id and not name else [ a.id for a in synophotos.albums( name ) ]
	for id in album_ids:
		pp( synophotos.unshare_album( id ) )

# finder for ids

@cli.command( 'id', help='helps finding ids of various things' )
@option( '-a', '--album', required=False, is_flag=True, help='search for album id' )
@option( '-f', '--folder', required=False, is_flag=True, help='search for folder id' )
@option( '-g', '--group', required=False, is_flag=True, help='search for group id' )
@option( '-u', '--user', required=False, is_flag=True, help='search for user id' )
@argument( 'element', nargs=1, required=True )
@pass_obj
def identify( ctx: ApplicationContext, element: str, user: bool, group: bool, album: bool, folder: bool ):
	if album:
		pp( synophotos.id_for_album( element ) )
	elif folder:
		pp( synophotos.id_for_folder( element ) )
	elif user:
		pp( synophotos.id_for_user( element ) )
	elif group:
		pp( synophotos.id_for_group( element ) )
	else:
		pp( '[bold]error[/bold]: use one of the parameters a/g/u to indicate what to identify' )

@cli.command( hidden=True, help='search for various things' )
@argument( 'name', nargs=1, required=True )
@pass_obj
def search( ctx: ApplicationContext, name: str ):
	pp( synophotos.search( name ) )

@cli.command( help='download items' )
@option( '-d', '--destination', required=True, help='destination folder for downloaded items' )
@option( '-s', '--size', required=False, default='original', help='download image in specified size, can be one of [sm, m, xl, original]' )
@argument( 'id', nargs=1, required=True )
@pass_obj
def download( ctx: ApplicationContext, destination: str, id: int, size: ThumbnailSize ):
	if size == 'original':
		size = 'xl'
		log.warning( 'download original size of images is currently broken, falling back to XL thumbnails' )

	fs = OSFS( root_path=destination, expand_vars=True, create=True )

	item, contents = synophotos.download( id, thumbnail=size )
	folder = synophotos.folder( item.folder_id )

	fs.makedirs( folder.name, recreate=True )
	fs.writebytes( path=f'{folder.name}/{item.filename}', contents=contents )
	log.info( f'downloaded item {item.id} to: {folder.name}/{item.filename}, wrote {len( contents )} bytes' )

@cli.command( help='displays information on items, folder and albums (this is mainly for development)' )
@option( '-a', '--album-id', required=False, is_flag=True, default=False, help='treat provided id as album id' )
@option( '-f', '--folder-id', required=False, is_flag=True, default=False, help='treat provided id as folder id' )
@option( '-i', '--item-id', required=False, is_flag=True, default=False, help='treat provided id as item id (this is the default)' )
@argument( 'id', nargs=1, required=False, type=int )
@pass_obj
def show( ctx: ApplicationContext, album_id: bool, folder_id, item_id: bool, id: int ):
	if not album_id and not folder_id and not item_id:
		item_id = True

	if item_id:
		print_obj_table( synophotos.item( id ) )
	elif album_id:
		print_obj_table( synophotos.album( id ) )
	elif folder_id:
		print_obj_table( synophotos.folder( id ) )


# noinspection PyShadowingNames
@cli.command( help='sync' )
# @option( '-a', '--album', required=False, is_flag=True, help='treat arguments as albums (the default)' ) # for now only sync albums
@option( '-d', '--destination', required=True, is_flag=False, help='destination folder to sync to' )
@argument( 'albums', nargs=-1, required=True )
@pass_obj
def sync( ctx: ApplicationContext, albums: List[str], destination: str ):
	fs = OSFS( root_path=destination, expand_vars=True, create=True )
	albums = flatten( [ synophotos.albums( a, include_shared=True ) for a in albums ] )
	albums = list( { a.id: a for a in albums }.values() ) # make unique
	for a in albums:
		items = synophotos.list_album_items( a.id )
		for i in items:
			if not fs.exists( path := f'/{a.id} - {a.name}/{i.filename}' ):
				item, contents = synophotos.download( item_id=i.id, passphrase=a.passphrase, thumbnail='xl' )
				fs.makedirs( dirname( path ), recreate=True )
				fs.writebytes( path, contents )
				log.info( f'saved image to {fs.getsyspath( path )}' )

@cli.command( hidden=True, help='displays a selected payload (this is for development only)' )
@argument( 'name', nargs=1, required=False )
@pass_obj
def payload( ctx: ApplicationContext, name: str ):
	from inspect import getmembers
	from sys import modules
	members = [(k, v) for k, v in getmembers( modules['synophotos.parameters.photos'] ) if not k.startswith( '__' ) and isinstance( v, dict )]
	members = sorted( members, key=lambda m: m[0] )

	if name:
		members = filter( lambda m: name.lower() in m[0].lower(), members )

	pp( table_for( [ 'name', 'payload' ], [ [k, v] for k, v in members ] ) )

@cli.command( help='prints version information' )
@pass_obj
def version( ctx: ApplicationContext ):
	pp( __version__ )

# helper

@cli.command( 'profile', help='shows the name of the currently active profile' )
@pass_obj
def profile( ctx: ApplicationContext ):
	pp( ctx.config.profile )

def _ws( ctx: ApplicationContext ) -> SynoPhotos:
	return cast( SynoPhotos, ctx.service )

def main( *args, **kwargs ):
	cli()  # trigger cli

if __name__ == '__main__':
	main()
