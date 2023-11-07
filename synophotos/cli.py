from logging import getLogger
from sys import exit as sysexit
from typing import cast, Optional

from click import argument, Context, group, option, pass_context, pass_obj

from synophotos import ApplicationContext
from synophotos.photos import SynoPhotos

log = getLogger( __name__ )

synophotos: Optional[SynoPhotos] = None  # global variable for functions below

@group
@option( '-d', '--debug', is_flag=True, required=False, help='outputs debug information' )
@pass_context
def cli( ctx: Context, debug: bool = False ):
	ctx.obj = ApplicationContext( debug=debug )

	# create (global) service (to ease login) and add to context
	global synophotos
	synophotos = SynoPhotos( url=ctx.obj.url, account=ctx.obj.account, password=ctx.obj.password, session=ctx.obj.session )
	ctx.obj.service = synophotos

	# attempt to log in
#	if not synophotos.login( ctx.obj ):
		# ctx.obj.console.print( f'error logging in code={syno_session.error_code}, msg={syno_session.error_msg}' )
#		ctx.obj.console.print( f'error logging in' )
#		sysexit( -1 )

# create

@cli.command( help='creates albums and folders' )
@option( '-a', '--album', required=False, is_flag=True, default=False, help='creates an album', type=bool )
@option( '-f', '--folder', required=False, is_flag=True, default=False, help='creates a folder', type=bool )
@option( '-ff', '--from-folder', required=False, help='id of folder to populate album with' )
@option( '-p', '--parent-id', required=False, default=0, help='parent id of the folder', type=int )
@option( '-s', '--share-with', required=False, help='share album with', type=int )
@argument( 'name', nargs=1, required=True )
@pass_obj
def create( ctx: ApplicationContext, album: bool, folder: bool,
            name: str, from_folder: int = None, parent_id: int = 0, share_with: int = None ):
	if album:
		album = synophotos.create_album( name )
		if from_folder:
			items = synophotos.list_items( from_folder, all_items=True, recursive=False )
			synophotos.add_album_items( album, items )
		ctx.console.print( album.id )
	elif folder:
		ctx.console.print( _ws( ctx ).create_folder( name, parent_id ) )

# count ... not sure if this is useful

@cli.command( 'count', help='counts various things' )
@option( '-a', '--albums', required=False, is_flag=True, default=False, help='counts the number of albums', type=bool )
@option( '-f', '--folders', required=False, is_flag=True, default=False, help='counts the number of folders', type=bool )
@option( '-i', '--items', required=False, is_flag=True, default=False, help='counts the number of items', type=bool )
@argument( 'parent_id', nargs=1, required=False, default=0, type=int )
@pass_obj
def count( ctx: ApplicationContext, albums: bool, folders: bool, items: bool, parent_id=0 ):
	if albums:
		ctx.console.print( synophotos.count_albums() )
	elif folders:
		ctx.console.print( synophotos.count_folders( parent_id ) )
	elif items:
		if albums:
			ctx.console.print( synophotos.count_items( album_id=parent_id ) )
		else:
			ctx.console.print( synophotos.count_items( folder_id=parent_id ) )
	else:
		ctx.console.print( 'error: provide one of the mandatory options -a, -f, -i or use --help to learn more' )

# list

@cli.command( help='lists objects' )
@option( '-a', '--albums', required=False, is_flag=True, default=False, help='lists albums', type=bool )
@option( '-f', '--folders', required=False, is_flag=True, default=False, help='lists folders', type=bool )
@option( '-g', '--groups', required=False, is_flag=True, default=False, help='lists groups', type=bool )
@option( '-i', '--items', required=False, is_flag=True, default=False, help='lists items', type=bool )
@option( '-p', '--parent_id', required=False, default=None, help='id of the parent (only valid when listing items or folders)', type=int )
@option( '-r', '--recursive', required=False, is_flag=True, default=False, help='include all folders recursively', type=bool )
@option( '-u', '--users', required=False, is_flag=True, default=False, help='lists users', type=bool )
@argument( 'name', nargs=1, required=False, type=str )
@pass_obj
def list( ctx: ApplicationContext, albums: bool, folders: bool, items: bool, groups: bool, users: bool,
          parent_id: int = None, name: str = None, recursive: bool = False ):
	if recursive:
		ctx.print( 'warning: fetching items without paging and/or recursively, this might take a while ...' )

	if albums:
		ctx.print( synophotos.list_albums( name ) )
	elif folders:
		ctx.print( synophotos.list_folders( parent_id, name, recursive ) )
	elif items:
		ctx.print( synophotos.list_items( parent_id, all_items=True, recursive=recursive ) )
	elif groups:
		ctx.print( synophotos.list_groups() )
	elif users:
		ctx.print( synophotos.list_users() )

@cli.command( help='gets the id of the root folder' )
@pass_obj
def root( ctx: ApplicationContext ):
	ctx.print( _ws( ctx ).root_folder().id )

# sharing

@cli.command( help='shares an album or folder' )
@option( '-a', '--album', required=False, is_flag=True, default=False, help='shares an album', type=bool )
@option( '-f', '--folder', required=False, is_flag=True, default=False, help='shares a folder', type=bool )
@option( '-n', '--album-name', required=False, help='name of the album to be created when sharing a folder' )
@option( '-r', '--role', required=False, default='view', help='permission role, can be "view", "download" or "upload"' )
@option( '-p', '--public', required=False, is_flag=True, help='shares an album publicly' )
@option( '-uid', '--user-id', required=False, help='shares an album with a user with the provided id' )
@option( '-gid', '--group-id', required=False, help='shares an album with a group with the provided id' )
@argument( 'id', nargs=1, required=True, type=int )
@pass_obj
def share( ctx: ApplicationContext, album: bool, folder: bool, id: int, album_name: str = None,
           role: str = 'view', public: bool = False, user_id: int = None, group_id: int = None ):
	if album:
		ctx.print( synophotos.share_album( id, role, public, user_id, group_id ).data )
	elif folder:
		ctx.print( synophotos.share_folder( id, album_name, role, public, user_id, group_id ).data )

@cli.command( help='unshares an album' )
@argument( 'album_id', nargs=1, required=True )
@pass_obj
def unshare( ctx: ApplicationContext, album_id: int ):
	ctx.print( synophotos.unshare_album( album_id ) )

# finder for ids

@cli.command( 'id', help='helps finding ids of various things' )
@option( '-a', '--album', required=False, is_flag=True, help='search for album id' )
@option( '-f', '--folder', required=False, is_flag=True, help='search for folder id' )
@option( '-g', '--group', required=False, is_flag=True, help='search for group id' )
@option( '-u', '--user', required=False, is_flag=True, help='search for user id' )
@argument( 'element', nargs=1, required=True )
@pass_obj
def find_id( ctx: ApplicationContext, element: str, user: bool, group: bool, album: bool, folder: bool ):
	if album:
		ctx.print( synophotos.id_for_album( element ) )
	elif folder:
		ctx.print( synophotos.id_for_folder( element ) )
	elif user:
		ctx.print( synophotos.id_for_user( element ) )
	elif group:
		ctx.print( synophotos.id_for_group( element ) )
	else:
		ctx.print( '[bold]error[/bold]: use one of the parameters a/g/u to indicate what to identify' )

@cli.command( help='search for various things' )
@argument( 'name', nargs=1, required=True )
@pass_obj
def search( ctx: ApplicationContext, name: str ):
	ctx.print( synophotos.search( name ) )

@cli.command( help='prints version information' )
@pass_obj
def version( ctx: ApplicationContext ):
	ctx.print( '0.1.0' )

# helper

@cli.command( 'profile', help='shows the name of the currently active profile' )
@pass_obj
def profile( ctx: ApplicationContext ):
	ctx.print( ctx.config.profile )

def _ws( ctx: ApplicationContext ) -> SynoPhotos:
	return cast( SynoPhotos, ctx.service )

def main( *args, **kwargs ):
	cli()  # trigger cli

if __name__ == '__main__':
	main()
