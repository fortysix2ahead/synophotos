
from enum import Enum
from typing import Dict


# todo: not sure if this can be structured in a nicer way, it feels like a lot of boilerplate stuff

# little helper for keywords to dict, to save minimal typing
def kwd( **kwargs ) -> Dict:
	return { **kwargs }

# enums to store different allowed 'field values'

class api( Enum ):
	browse_album='SYNO.Foto.Browse.Album'
	browse_folder='SYNO.Foto.Browse.Folder'
	browse_item='SYNO.Foto.Browse.Item'
	download='SYNO.Foto.Download'
	download_shared='SYNO.FotoTeam.Download'
	sharing_passphrase='SYNO.Foto.Sharing.Passphrase'
	thumbnail='SYNO.Foto.Thumbnail'
	thumbnail_shared='SYNO.FotoTeam.Thumbnail'

class category( Enum ):
	normal='normal'
	normal_share_with_me='normal_share_with_me'

class sort_by( Enum ):
	create_time='create_time'
	takentime='takentime'

class sort_direction( Enum ):
	asc='asc'
	desc='desc'

# dicts of default values from enums from above

API_BROWSE_ALBUM = { api.__name__: api.browse_album.value }
API_BROWSE_FOLDER = { api.__name__: api.browse_folder.value }
API_BROWSE_ITEM = { api.__name__: api.browse_item.value }
API_DOWNLOAD = { api.__name__: api.download.value }
API_DOWNLOAD_SHARED = { api.__name__: api.download_shared.value }
API_SHARING_PASSPHRASE = { api.__name__: api.sharing_passphrase.value }
API_THUMBNAIL = { api.__name__: api.thumbnail.value }
API_THUMBNAIL_SHARED = { api.__name__: api.thumbnail_shared.value }

SORT_CREATE_TIME = { sort_by.__name__: sort_by.create_time.value }
SORT_TAKENTIME = { sort_by.__name__: sort_by.takentime.value }
SORT_ASC = { sort_direction.__name__: sort_direction.asc.value }

CAT_NORMAL = { category.__name__: category.normal.value }
CAT_SHARED = { category.__name__: category.normal_share_with_me.value }

# urls

BROWSE_NORMAL_ALBUM_URL = '{url}/entry.cgi/SYNO.Foto.Browse.NormalAlbum'

# SID is always necessary

SID = { 'format': 'sid', '_sid': None }

# parameter sets for various operations, this is very basic stuff
# unfortunately the version seems to depend on DSM version (or even client application versions)

COUNT = { 'method': 'count', 'version': 1 }
CREATE = { 'method': 'create', 'version': 1 }
DOWNLOAD1 = { 'method': 'download', 'version': 1 }
DOWNLOAD2 = { 'method': 'download', 'version': 2 }
GET1 = { 'method': 'get', 'version': 1 }
GET2 = { 'method': 'get', 'version': 2 }
GET4 = { 'method': 'get', 'version': 4 }
GET5 = { 'method': 'get', 'version': 5 }
GET_EXIF1 = { 'method': 'get_exif', 'version': 1 }
LIST2 = { 'method': 'list', 'version': 2, 'offset': 0, 'limit': 5000 } # todo: not sure about limits, these may vary depending on items/folders/albums
LIST4 = { 'method': 'list', 'version': 4, 'offset': 0, 'limit': 100 }
SET_SHARED1 = { 'method': 'set_shared', 'version': 1 }
UPDATE1 = { 'method': 'update', 'version': 1 }

# get elements

GET_ALBUM = API_BROWSE_ALBUM | GET4 | { 'id': '[0]', 'additional': '["sharing_info","flex_section","provider_count","thumbnail"]' }
GET_FOLDER = API_BROWSE_FOLDER | GET2 | { 'id': ..., 'additional': '["access_permission"]' } # id is an int, not a list!
GET_SHARED_ALBUM = API_BROWSE_ALBUM | GET4 | { 'passphrase': ..., 'additional': '["sharing_info","flex_section","provider_count","thumbnail"]' } # id is missing in favour of the passphrase!
GET_ITEM = API_BROWSE_ITEM | GET5 | {
	'id': '[0]',
	'additional': '["description","tag","exif","resolution","orientation","gps","video_meta","video_convert","thumbnail","address","geocoding_id","rating","motion_photo","provider_user_id","person"]'
}
GET_SHARED_ITEM = API_BROWSE_ITEM | GET5 | {
	'id': '[...]',
	'passphrase': ...,
	'additional': '["description","tag","exif","resolution","orientation","gps","video_meta","video_convert","thumbnail","address","geocoding_id","rating","motion_photo","provider_user_id","person"]'
}
GET_EXIF = API_BROWSE_ITEM | GET_EXIF1 | { 'id': '[...]' }

# download item

DOWNLOAD_ORIGINAL = API_DOWNLOAD | DOWNLOAD2 | { 'force_download': 'true', 'item_id': '[0]', 'download_type': 'source' }
DOWNLOAD_COMPRESSED = API_DOWNLOAD | DOWNLOAD2 | { 'force_download': 'true', 'item_id': '[0]', 'download_type': 'optimized_jpeg' }
DOWNLOAD_SHARED_ORIGINAL = API_DOWNLOAD | DOWNLOAD2 | { 'force_download': 'true', 'item_id': '[0]', 'download_type': 'source', 'passphrase': ... }
DOWNLOAD_COMPRESSED_ORIGINAL = API_DOWNLOAD | DOWNLOAD2 | { 'force_download': 'true', 'item_id': '[0]', 'download_type': 'optimized_jpeg', 'passphrase': ... }

# both outdated ??
DOWNLOAD_ITEM = API_DOWNLOAD | GET1 | { 'mode': 'download', 'id': ..., 'type': 'source' }
DOWNLOAD_SHARED_ITEM = API_DOWNLOAD_SHARED | DOWNLOAD1 | { 'unit_id': '"[...]"', 'cache_key': ... } # + cache_key="40808_1633659236" ???

DOWNLOAD_THUMBNAIL = API_THUMBNAIL | GET1 | { 'mode': 'download', 'id': ..., 'type': 'unit', 'size': 'xl', 'cache_key': ... }
DOWNLOAD_SHARED_THUMBNAIL = API_THUMBNAIL | GET2 | { 'id': ..., 'type': 'unit', 'size': 'xl', 'cache_key': ..., 'passphrase': ... }

# browse/list elements

BROWSE_ALBUM = { **API_BROWSE_ALBUM, **CAT_NORMAL, **LIST4, }
BROWSE_ALBUM_ALL = { **API_BROWSE_ALBUM, **SORT_ASC, **CAT_SHARED, **LIST4, }
BROWSE_FOLDER = API_BROWSE_FOLDER | LIST2 | SORT_ASC | { 'id': 0 }
BROWSE_ITEM = { 'api': 'SYNO.Foto.Browse.Item', 'sort_by': 'filename', **SORT_ASC, **LIST4, }

LIST_ALBUM = API_BROWSE_ALBUM | LIST4 | CAT_SHARED | SORT_ASC | { 'additional': '["sharing_info"]' }
LIST_SHARED_ITEMS = API_BROWSE_ITEM | LIST4 | SORT_ASC | SORT_TAKENTIME | { 'passphrase': '""' }

# search elements

# keyword needs to be filled out
SEARCH_COUNT_ITEM = { 'api': 'SYNO.Foto.Search.Search', 'method': 'count_item', 'version': '2', 'keyword': '', **SID, }
SEARCH_ITEM = {
	'api': 'SYNO.Foto.Search.Search',
	'method': 'list_item',
	'version': '2',
	'offset': '0',
	'limit': '20',
#	'additional': '["thumbnail","resolution","orientation","video_convert","video_meta","address"]',
#	'timeline_group_unit': '"day"', # webapi only?
	'keyword': '',
#	'start_time': '1250294400', # webapi only?
#	'end_time': '1250380799', # webapi only?
	**SID,
}

# count elements

COUNT_ALBUM = { 'api': 'SYNO.Foto.Browse.Album', **COUNT, }
COUNT_FOLDER = { 'api': 'SYNO.Foto.Browse.Folder', 'id': 0, **COUNT, }
COUNT_ITEM = { 'api': 'SYNO.Foto.Browse.Item', **COUNT, }
COUNT_ITEM_FOLDER = { 'folder_id': 0, **COUNT_ITEM, }
COUNT_ITEM_ALBUM = { 'album_id': 0, **COUNT_ITEM, }

#

CREATE_ALBUM = {
    **CREATE,
    'api': 'SYNO.Foto.Browse.NormalAlbum',
    'name': None,
    # this should be '[1,2,3]' with the numbers being item ids,
    # but can be empty as well (although the Web UI does not allow that)
    'item': '[]',
}

CREATE_FOLDER = {
    **CREATE,
    'api': 'SYNO.Foto.Browse.Folder',
    'target_id': None, # id of the parent folder
    'name': None, # name of the folder
}

ADD_ITEM_TO_ALBUM = {
    'api': 'SYNO.Foto.Browse.NormalAlbum',
    'method': 'add_item',
    'version': 1,
    'id': 0,
    'item': '[]' # should be '[1,2,3]'
}

LIST_USER_GROUP = {
    **SID,
	'api': 'SYNO.Foto.Sharing.Misc',
	'method': 'list_user_group',
	'version': 1,
	'team_space_sharable_list': 'false'
}

SHARE_ALBUM = API_SHARING_PASSPHRASE | SET_SHARED1 | {'policy': 'album', 'album_id': 0, 'enabled': 'true' }

# passphrase: \"-escaped string, is created when sharing an album, probably contains encoded album_id + policy
# expiration: unknown what is meant by 0, maybe seconds to expiration or unix timestamp to expiration?
# permission: # this is a json string, with " escaped as \", for samples see below
UPDATE_PERMISSION = API_SHARING_PASSPHRASE | UPDATE1 | { 'passphrase': None, 'expiration': 0, 'permission': None }

__SAMPLE_PERMISSION = [{
    'role': 'view',
    'action': 'update',
    'member': {
        'type': 'user',
        'id': 1000 # this needs to be an int, otherwise error 120 will be returned
    }
}]

__SAMPLE_PERMISSION_STR = r'[{\"role\": \"view\", \"action\": \"update\", \"member\": {\"type\": \"user\", \"id\": 1000}}]'
__SAMPLE_PERMISSION_STR2 = r'"[{\"role\":\"download\",\"action\":\"update\",\"member\":{\"type\":\"user\",\"id\":1000}},{\"role\":\"view\",\"action\":\"update\",\"member\":{\"type\":\"user\",\"id\":1001}}]"'
