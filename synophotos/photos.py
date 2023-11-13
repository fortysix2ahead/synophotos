from __future__ import annotations

from logging import getLogger
from typing import List, Literal, Optional, Tuple

from attrs import define, field
from cattrs import Converter
from cattrs.preconf.json import make_converter
from more_itertools import first

from synophotos.parameters.photos import *
from synophotos.parameters.webservice import ENTRY_URL
from synophotos.webservice import SynoResponse, SynoWebService

log = getLogger( __name__ )

ThumbnailSize = Literal['sm', 'm', 'xl', 'original']

conv = Converter()
jconv = make_converter()

# photos-related dataclasses

@define
class Additional:
	access_permission: Dict = field( default=None ) # folder only?
	description: str = field( default=None )
	exif: Dict = field( factory=dict )
	flex_section: List[int] = field( factory=list ) # album only?
	orientation: int = field( default=None )
	orientation_original: int = field( default=None )
	person: List = field( default=list ) # that's of type class???
	provider_count: int = field( default=None )
	rating: int = field( default=None )
	resolution: Dict[str, int] = field( factory=dict )
	sharing_info: Dict = field( factory=dict ) # album only?
	tag: List[str] = field( factory=list )
	thumbnail: Dict = field( factory=dict )

@define
class Item:
	filename: str = field( default=None )
	filesize: int = field( default=None )
	folder_id: int = field( default=None )
	id: int = field( default=None )
	owner_user_id: int = field( default=None )
	time: int = field( default=None )
	indexed_time: int = field( default=None )
	type: str = field( default=None )
	live_type: str = field( default=None )
	additional: Additional = field( factory=Additional )

	# additional fields
	# folder: Folder = field( init=False, default=None )
	# albums: List[Album] = field( init=False, default_factory=list )

	@classmethod
	def table_fields( cls ) -> List[str]:
		return ['id', 'filename', 'filesize', 'folder_id', 'owner_user_id']


@define
class Folder:

	name: str = field( default=None )
	id: int = field( default=None )
	parent: int = field( default=None )
	owner_user_id: int = field( default=None )
	passphrase: Optional[str] = field( default=None )
	shared: bool = field( default=False )
	sort_by: str = field( default=None )
	sort_direction: str = field( default=None )

	additional: Dict[str, Dict[str, bool]] = field( factory=dict )

	# additional fields
	# items: List[Item] = field( init=False, default_factory=list )
	# subfolders: List[Folder] = field( init=False, default_factory=list )

	# metadata for table printing -> we're doing this via classmethod
	# table_fields: ClassVar[List[str]] = field( default=[ 'id', 'name' ] )

	@classmethod
	def table_fields( cls ) -> List[str]:
		return ['id', 'folder_name', 'path', 'parent', 'owner_user_id', 'shared']

	# additional properties

	@property
	def folder_name( self ) -> str:
		return self.name.rsplit( '/', 1 )[1]

	@property
	def path( self ) -> str:
		return s if (s := self.name.rsplit( '/', 1 )[0]) else '/'

	@property
	def is_root( self ) -> bool:
		return True if self.id == self.parent else False


@define
class Album:
	name: str = field( default=None )
	id: int = field( default=0 )
	shared: bool = field( default=False )
	temporary_shared: bool = field( default=False )
	cant_migrate_condition: Dict = field( default=None )
	condition: Dict = field( default=None )
	create_time: int = field( default=0 )
	end_time: int = field( default=0 )
	freeze_album: bool = field( default=False )
	item_count: int = field( default=0 )
	owner_user_id: int = field( default=0 )
	passphrase: str = field( default=None )
	sort_by: str = field( default=None )
	sort_direction: str = field( default=None )
	start_time: int = field( default=0 )
	type: str = field( default=None )
	version: int = field( default=0 )

	# for album this can be ["sharing_info","flex_section","provider_count","thumbnail"]
	additional: Additional = field( factory=Additional )

	# additional fields
	# items: [] = field( init=False, default_factory=list )

	@classmethod
	def table_fields( cls ) -> List[str]:
		return ['id', 'name', 'item_count', 'owner_user_id', 'shared']

	def is_shared( self ) -> bool:
		return self.shared or self.temporary_shared

@define
class Member:
	type: str = field( default='user' )  # 'user' or 'group'
	id: int = field( default=0 )  # id of the user or group

@define
class Permission:
	role: str = field( default='view' )  # can be 'download', 'view' and 'upload'
	action: str = field( default='update' )  # 'update' ... what else is possible?
	member: Member = field( factory=Member )  # this cannot be None

	@classmethod
	def as_str( cls, permissions: List[Permission] ) -> str:
		return jconv.dumps( permissions )

# class for photos

@define
class SynoPhotos( SynoWebService ):

	# counting elements

	def count_albums( self ) -> int:
		return self.get( ENTRY_URL, COUNT_ALBUM ).data.get( 'count' )

	def count_folders( self, parent_id: int = 0 ) -> int:
		return self.get( ENTRY_URL, {**COUNT_FOLDER, 'id': parent_id} ).data.get( 'count' )

	def count_items( self, folder_id: int = None, album_id: int = None ) -> int:
		if folder_id:
			return self.get( ENTRY_URL, {**COUNT_ITEM, 'folder_id': folder_id} ).data.get( 'count' )
		elif album_id:
			return self.get( ENTRY_URL, {**COUNT_ITEM, 'album_id': album_id} ).data.get( 'count' )
		else:
			return self.get( ENTRY_URL, COUNT_ITEM ).data.get( 'count' )

	# listing elements

	def list_albums( self, name: str = None, include_shared: bool = False ) -> List[Album]:
		payload = BROWSE_ALBUM if not include_shared else BROWSE_ALBUM_ALL
		albums = self.entry( payload ).as_list( Album )
		albums = [a for a in albums if name.lower() in a.name.lower()] if name else albums
		return sorted( albums, key=lambda a: a.name )

	def list_folders( self, parent_id: int = None, name: str = None, recursive: bool = False ) -> List[Folder]:
		if parent_id in [None, 0]:
			parent_id = self.root_folder().id

		folders = []
		if recursive:
			root = self.folder( parent_id )
			queue = [root]
			while len( queue ) > 0:
				parent = queue.pop( 0 )
				children = self.entry( {**BROWSE_FOLDER, 'id': parent.id} ).as_list( Folder )
				folders.extend( children )
				queue.extend( children )
		else:
			folders = self.get( ENTRY_URL, {**BROWSE_FOLDER, 'id': parent_id} ).as_list( Folder )

		if name:
			folders = list( filter( lambda f: name.lower() in f.name.lower(), folders ) )

		folders = sorted( folders, key=lambda f: f.folder_name )

		return folders

	def list_album_items( self, album_id: int = None ) -> List[Item]:
		items, limit, offset = [], BROWSE_ITEM.get( 'limit' ), BROWSE_ITEM.get( 'offset' )

		if album_id:
			albums = self.list_albums( include_shared=True )
			album = next( ( a for a in albums if a.id == album_id ), None )

			while True:
				if album.shared and album.passphrase:
					page = self.entry( {**LIST_SHARED_ITEMS, 'limit': limit, 'offset': offset, 'passphrase': f'"{album.passphrase}"'} ).as_list( Item )
				else:
					page = self.entry( {**BROWSE_ITEM, 'album_id': album_id, 'limit': limit, 'offset': offset} ).as_list( Item )

				if page:
					items.extend( page )
					offset = offset + limit
				else:
					break

		return items

	def list_folder_items( self, folder_id: int = None, recursive: bool = False ) -> List[Item]:
		items, limit, offset = [], BROWSE_ITEM.get( 'limit' ), BROWSE_ITEM.get( 'offset' )

		parent_ids = [folder_id]
		if recursive:
			parent_ids.extend( [p.id for p in self.list_folders( folder_id, recursive=True )] )

		for folder_id in parent_ids:
			while True:
				if page := self.entry( {**BROWSE_ITEM, 'folder_id': folder_id, 'limit': limit, 'offset': offset} ).as_list( Item ):
					items.extend( page )
					offset = offset + limit
				else:
					break

		return items

	def list_items( self, album_id: int = None, folder_id: int = None, recursive: bool = False, name: str = None ) -> List[Item]:
		if not album_id and not folder_id:
			folder_id = self.root_folder().id

		if album_id:
			items = self.list_album_items( album_id )
		elif folder_id:
			items = self.list_folder_items( folder_id, recursive )
		else:
			items = []

		items = list( filter( lambda i: name.lower() in i.filename.lower(), items ) ) if name else items
		return items

	def list_groups( self ):
		response = self.get( ENTRY_URL, LIST_USER_GROUP ).data.get( 'list' )
		response = [e for e in response if e.get( 'type' ) == 'group']
		return response

	def list_users( self ):
		response = self.get( ENTRY_URL, LIST_USER_GROUP ).data.get( 'list' )
		response = [e for e in response if e.get( 'type' ) == 'user']
		return response

	# search for elements

	def search( self, term: str ):
		return self.get( ENTRY_URL, {**SEARCH_ITEM, 'keyword': term} ).data.get( 'list' )

	# create functionality

	def create_album( self, name: str ) -> Album:
		return self.get( ENTRY_URL, {**CREATE_ALBUM, 'name': name} ).as_obj( Album )

	def create_folder( self, name: str, parent_id: int = 0 ) -> int:
		return self.get( ENTRY_URL, {**CREATE_FOLDER, 'name': f'\"{name}\"', 'target_id': parent_id} )

	def download( self, item_id: int, thumbnail: Optional[ThumbnailSize] = None ) -> Tuple[Item, bytes]:
		_item, binary = self.item( item_id ), b''
		if thumbnail:
			response = self.entry( DOWNLOAD_THUMBNAIL, id=item_id, cache_key=_item.additional.thumbnail.get( 'cache_key' ) )
			binary = response.response.content
		else:
			raise NotImplementedError

		return _item, binary

	# helpers

	def album( self, id: int ) -> Album:
		album = first( self.entry( GET_ALBUM, id=f'[{id}]' ).as_obj( List[Album] ), None )
		if not album: # no album, try again with shared albums
			albums = self.list_albums( name=None, include_shared=True )
			if album := first( [a for a in albums if id == a.id], None ):
				album = first( self.entry( GET_SHARED_ALBUM, passphrase=album.passphrase ).as_obj( List[Album] ) )
		return album

	def albums( self, name: str ) -> List[Album]:
		return self.list_albums( name, include_shared=False )

	def folder( self, id: int ) -> Folder:
		return self.entry( GET_FOLDER, id=id ).as_obj( Folder )

	def folders( self, name: str ) -> List[Folder]:
		return self.list_folders( 0, name, True )

	def item( self, id: int ) -> Optional[Item]:
		return first( self.entry( GET_ITEM, id=f'[{id}]' ).as_obj( List[Item] ), None )

	def root_folder( self ) -> Folder:
		return self.folder( 0 )

	def add_album_items( self, album: Album, items: List[Item] ) -> None:
		item_ids = [str( i.id ) for i in items]
		item_ids_str = f'[{",".join( item_ids )}]'
		self.get( ENTRY_URL, {**ADD_ITEM_TO_ALBUM, 'id': album.id, 'item': item_ids_str} )

	def id_for_user( self, user: str ) -> int:
		return next( (d.get( 'id' ) for d in self.list_users() if (d.get( 'name' ) == user and d.get( 'type' ) == 'user')), None )

	def id_for_group( self, group: str ) -> int:
		return next( (d.get( 'id' ) for d in self.list_groups() if (d.get( 'name' ) == group and d.get( 'type' ) == 'group')), None )

	def id_for_album( self, album: str ) -> int:
		return next( (a.id for a in self.list_albums( album, True ) if album.lower() in a.name.lower()), None )

	def id_for_folder( self, folder: str ) -> int:
		return next( (f.id for f in self.list_folders( 0, folder, True )), None )

	# sharing

	def share_album( self, album_id: int, role: str, public: bool, user_id: int, group_id: int ) -> Optional[SynoResponse]:
		if not public and not user_id and not group_id:
			return

		response = self.entry( SHARE_ALBUM, album_id=album_id, enabled='true' )

		if public:
			permissions = [Permission( role=role, member=Member( type='public' ) )]
		elif user_id:
			permissions = [Permission( role=role, member=Member( type='user', id=user_id ) )]
		elif group_id:
			permissions = [Permission( role=role, member=Member( type='group', id=group_id ) )]
		else:
			permissions = None

		if permissions:
			return self.grant_permission( permissions, response.data.get( 'passphrase' ) )

	def share_folder( self, folder_id: int, album_name: str, role: str, public: bool, user_id: int, group_id: int ):
		folder = self.folder( folder_id )
		album_name = album_name if album_name else folder.name.split( '/' )[-1]
		album = self.create_album( album_name )
		self.add_album_items( album, self.list_items( folder_id, True, False ) )
		return self.share_album( album.id, role, public, user_id, group_id )

	def grant_permission( self, permissions: List[Permission], passphrase: str ) -> SynoResponse:
		return self.entry( UPDATE_PERMISSION, permission=Permission.as_str( permissions ), passphrase=f'"{passphrase}"' )

	def unshare_album( self, album_id: int ) -> SynoResponse:
		return self.entry( SHARE_ALBUM, album_id=album_id, enabled='false' )

