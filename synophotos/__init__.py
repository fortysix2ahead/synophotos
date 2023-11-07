from dataclasses import dataclass, field
from json import dumps, loads
from logging import DEBUG, getLogger, WARNING
from pathlib import Path
from sys import exit as sysexit
from typing import Any, Dict, Optional, TypeVar, Union

from platformdirs import user_config_dir
from rich.console import Console
from rich.logging import RichHandler

from synophotos.ui import dataclass_table
from synophotos.webservice import SynoSession, WebService

T = TypeVar('T')

USER_CFG_DIR = Path( user_config_dir( 'synocli', roaming=True ) )

CONFIG_FILE = 'config.json'
PROFILES_FILE = 'profiles.json'
SESSIONS_FILE = 'sessions.json'

# create root logger
log = getLogger( __name__ )

LOG_CONSOLE_DEBUG_HANDLER = RichHandler( level=DEBUG, show_time=True, show_level=True, markup=True, log_time_format='%H:%M:%S' )
LOG_CONSOLE_DEFAULT_HANDLER = RichHandler( level=WARNING, show_time=False, show_level=False, markup=True )

# configure logger
def activate_log_handler( debug: bool = False ):
	log.handlers.clear()
	if debug:
		log.setLevel( DEBUG )
		log.addHandler( LOG_CONSOLE_DEBUG_HANDLER )
	else:
		log.setLevel( WARNING )
		log.addHandler( LOG_CONSOLE_DEFAULT_HANDLER )

activate_log_handler() # activate default log handler

@dataclass
class Config:

	profile: str = field( default=None )
	debug: bool = field( default=False )

@dataclass
class Profile:

	url: str = field( default=None )
	account: str = field( default=None )
	password: str = field( default=None )

@dataclass
class ApplicationConfiguration:

	config: Config = field( default=Config() )
	profiles: Dict[str, Profile] = field( default_factory=dict )
	sessions: Dict[str, SynoSession] = field( default_factory=dict )

	debug: bool = field( default=False )

	def save_sessions( self ) -> None:
		with Path( USER_CFG_DIR, SESSIONS_FILE ) as f:
			f.write_text( dumps( FACTORY.dump( self.sessions, Dict[str, SynoSession] ), indent=2 ), encoding='UTF-8' )

	@property
	def profile( self ) -> Profile:
		return self.profiles.get( self.config.profile )

	@property
	def session( self ) -> SynoSession:
		return self.sessions.get( self.config.profile )

@dataclass
class ApplicationContext:

	cfg: ApplicationConfiguration = field( default=ApplicationConfiguration() )
	service: WebService = field( default=None )

	url: str = field( default=None )
	account: str = field( default=None )
	password: str = field( default=None )

	debug: bool = field( default=None )

	console: Console = field( default=Console() )

	def __post_init__( self ):
		self.__load_config_files()

		self.debug = self.debug if self.debug is not None else self.cfg.debug

		# todo: allow override url/account/password

		# reconfigure log handler
		if self.debug:
			activate_log_handler( debug=True )

	def __load_config_files( self ):
		with Path( USER_CFG_DIR ) as ucd:
			self.cfg.config = self.__load_file( ucd, CONFIG_FILE, True, Config )
			self.cfg.profiles = self.__load_file( ucd, PROFILES_FILE, True, Dict[str, Profile] )
			self.cfg.sessions = self.__load_file( ucd, SESSIONS_FILE, False, Dict[str, SynoSession] )

	def __load_file( self, parent: Path, filename: str, exit_on_fail: bool, cls: T = None ) -> Optional[Union[Dict, T]]:
		try:
			with Path( parent, filename ) as file:
				json = loads( file.read_text( encoding='UTF-8' ) )
				return FACTORY.load( json, cls ) if cls else json
		except FileNotFoundError:
			self.console.print( f'Error reading {file}' )
			log.debug( 'unable to read file', exc_info=True )
			if exit_on_fail:
				sysexit( -1 )
			return None

	# helpers

	def print( self, obj: Any ) -> None:
		if isinstance( obj, list ):
			self.console.print( dataclass_table( obj ) )
		else:
			self.console.print( obj )
