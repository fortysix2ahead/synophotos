
from logging import DEBUG, WARNING, getLogger
from sys import exit as sysexit
from typing import Any, Dict, Optional, Type, TypeVar

from attrs import define, field
from cattrs.preconf.pyyaml import make_converter
from fs.errors import ResourceNotFound
from fs.osfs import OSFS
from platformdirs import user_config_dir
from rich.console import Console
from rich.logging import RichHandler

from synophotos.ui import dataclass_table
from synophotos.webservice import SynoSession, WebService

log = getLogger( __name__ )

T = TypeVar('T')

APPNAME = 'synophotos'

CFG_DIR = user_config_dir( appname=APPNAME, roaming=True )
CFG_FS = OSFS( root_path=CFG_DIR )

CONFIG_FILE = 'config.yaml'
PROFILES_FILE = 'profiles.yaml'
SESSIONS_FILE = 'sessions.yaml'

CONVERTER = make_converter()

LOG_CONSOLE_DEBUG_HANDLER = RichHandler( level=DEBUG, show_time=True, show_level=True, markup=True, log_time_format='%H:%M:%S' )
LOG_CONSOLE_DEFAULT_HANDLER = RichHandler( level=WARNING, show_time=False, show_level=False, markup=True )

def activate_log_handler( debug: bool = False ):
	log.handlers.clear()
	if debug:
		log.setLevel( DEBUG )
		log.addHandler( LOG_CONSOLE_DEBUG_HANDLER )
	else:
		log.setLevel( WARNING )
		log.addHandler( LOG_CONSOLE_DEFAULT_HANDLER )

activate_log_handler() # activate default log handler

@define
class Config:

	profile: str = field( default=None )
	debug: bool = field( default=False )

@define
class Profile:

	url: str = field( default=None )
	account: str = field( default=None )
	password: str = field( default=None )

@define
class ApplicationContext:

	profiles: Dict[str, Profile] = field( factory=dict )
	config: Config = field( default=None )
	sessions: Dict[str, SynoSession] = field( factory=dict )

	debug: bool = field( default=None )

	service: WebService = field( default=None )
	console: Console = field( default=Console() ) # todo: move this somewhere else

	def __attrs_post_init__( self ):
		self.__load_config_files()

		# reconfigure log handler
		if self.debug:
			activate_log_handler( debug=True )

	def __load_config_files( self ):
		self.profiles = self.__load_file( PROFILES_FILE, Dict[str, Profile] )
		self.config = self.__load_file( CONFIG_FILE, Config )
		self.sessions = self.__load_file( SESSIONS_FILE, Dict[str, SynoSession], False )

	# noinspection PyMethodMayBeStatic
	def __load_file( self, filename: str, cls: Type[T] = None, exit_on_fail: bool = True ) -> Optional[T]:
		try:
			return CONVERTER.loads( CFG_FS.readtext( filename ), cls )
		except ResourceNotFound:
			log.error( f'unable to read file {filename}', exc_info=True )
			if exit_on_fail:
				sysexit( -1 )
			return {}

	@property
	def url( self ) -> str:
		return self.profiles.get( self.config.profile ).url

	@property
	def account( self ) -> str:
		return self.profiles.get( self.config.profile ).account

	@property
	def password( self ) -> str:
		return self.profiles.get( self.config.profile ).password

	@property
	def session( self ) -> SynoSession:
		return self.sessions.get( self.config.profile )

	# helpers

	def print( self, obj: Any ) -> None:
		if isinstance( obj, list ):
			self.console.print( dataclass_table( obj ) )
		else:
			self.console.print( obj )
