"""Synophotos - Synology Photos Command Line Interface"""

from logging import DEBUG, INFO, WARNING, getLogger
from sys import exit as sysexit
from typing import Dict, Optional, Type, TypeVar

from attrs import define, field
from cattrs.preconf.pyyaml import make_converter
from fs.errors import ResourceNotFound
from fs.osfs import OSFS
from platformdirs import user_config_dir
from rich.logging import RichHandler

from synophotos.ui import dataclass_table
from synophotos.webservice import SynoSession, WebService

__version__ = '0.1.2'

log = getLogger( __name__ )

T = TypeVar('T')

APPNAME = 'synophotos'

CFG_DIR = user_config_dir( appname=APPNAME, roaming=True )
CFG_FS = OSFS( root_path=CFG_DIR, create=True, expand_vars=True )

CONFIG_FILE = 'config.yaml'
SESSIONS_FILE = 'sessions.yaml'

DEFAULT_CONFIG = {
	'profile': 'sample_profile',
	'profiles': {
		'sample_profile': {
			'url': 'https://synology.photos.sample.server.example.com',
			'account': 'sample_account',
			'password': 'sample_password',
		}
	}
}

CONVERTER = make_converter()

# logging

DISABLE = 100
DEFAULT_HANDLER = RichHandler( level=WARNING, show_time=False, show_level=False, markup=True )
VERBOSE_HANDLER = RichHandler( level=INFO, show_time=True, show_level=False, markup=True, log_time_format='%H:%M:%S' )
DEBUG_HANDLER = RichHandler( level=DEBUG, show_time=True, show_level=True, markup=True, log_time_format='%H:%M:%S.%f', omit_repeated_times=False )

log.addHandler( DEFAULT_HANDLER )
log.addHandler( VERBOSE_HANDLER )
log.addHandler( DEBUG_HANDLER )

@define
class Profile:

	url: str = field( default=None )
	account: str = field( default=None )
	password: str = field( default=None )

@define
class Config:

	debug: bool = field( default=False )
	force: bool = field( default=False )
	verbose: bool = field( default=False )

	profile: str = field( default=None )
	profiles: Dict[str, Profile] = field( factory=dict )

	@property
	def active_profile( self ) -> Optional[Profile]:
		return self.profiles.get( self.profile )

@define
class ApplicationContext:

	config: Config = field( factory=Config )
	sessions: Dict[str, SynoSession] = field( factory=dict )

	debug: bool = field( default=False )
	force: bool = field( default=False )
	verbose: bool = field( default=False )

	service: WebService = field( default=None )

	def __attrs_post_init__( self ):
		self.__configure_log__()
		self.__load_config_files()

	def __configure_log__( self ):
		global DEFAULT_HANDLER, VERBOSE_HANDLER, DEBUG_HANDLER
		if self.debug:
			DEBUG_HANDLER.setLevel( DEBUG )
			VERBOSE_HANDLER.setLevel( DISABLE )
			DEFAULT_HANDLER.setLevel( DISABLE )
			log.setLevel( DEBUG )
		elif self.verbose:
			DEBUG_HANDLER.setLevel( DISABLE )
			VERBOSE_HANDLER.setLevel( INFO )
			DEFAULT_HANDLER.setLevel( DISABLE )
			log.setLevel( INFO )
		else:
			DEBUG_HANDLER.setLevel( DISABLE )
			VERBOSE_HANDLER.setLevel( DISABLE )
			DEFAULT_HANDLER.setLevel( WARNING )
			log.setLevel( WARNING )

	def __load_config_files( self ):
		self.config = self.__load_file( CONFIG_FILE, Config, exit_on_fail=False )
		# self.sessions = self.__load_file( SESSIONS_FILE, Dict[str, SynoSession], False )

	# noinspection PyMethodMayBeStatic
	def __load_file( self, filename: str, cls: Type[T] = None, exit_on_fail: bool = True ) -> Optional[T]:
		try:
			return CONVERTER.loads( CFG_FS.readtext( filename ), cls )
		except ResourceNotFound:
			log.debug( f'unable to read file {filename}', exc_info=True )
			if exit_on_fail:
				sysexit( -1 )
			return Config()

	@property
	def url( self ) -> str:
		return self.config.active_profile.url

	@property
	def account( self ) -> str:
		return self.config.active_profile.account

	@property
	def password( self ) -> str:
		return self.config.active_profile.password

	@property
	def session( self ) -> SynoSession:
		return self.sessions.get( self.config.profile )
