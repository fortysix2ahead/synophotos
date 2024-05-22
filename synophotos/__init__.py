"""Synophotos - Synology Photos Command Line Interface"""

from logging import DEBUG, INFO, WARNING, getLogger
from typing import Dict, Optional, TypeVar

from attrs import define, field
from click import get_current_context
from dynaconf import Dynaconf
from dynaconf.vendor.box.exceptions import BoxKeyError
from fs.appfs import UserConfigFS
from fs.errors import ResourceNotFound
from rich.logging import RichHandler

from synophotos.cache import Cache, dumps as dump_cache, loads as load_cache
from synophotos.ui import dataclass_table
from synophotos.webservice import SynoSession, SynoSessions, WebService

log = getLogger( __name__ )

T = TypeVar('T')

__version__ = '0.3.0-dev'
__author__ = 'fortysix2ahead'
__author_email__ = 'fortysix2ahead@gmail.com'
__license__ = 'MIT'

APPNAME = 'synophotos'
APP_PKG_NAME = 'synophotos'
CONFIG_FILE = 'config.yaml'
SESSIONS_FILE = 'sessions.yaml'
CACHE_FILE = 'cache.yaml'
SAMPLE_SETTINGS_FILE = 'settings-sample.yaml'
SETTINGS_FILE = 'settings.yaml'

CFG_FS = UserConfigFS( APPNAME, roaming=True, create=True )

SETTINGS: Dynaconf = Dynaconf( envvar_prefix = 'SYNOPHOTOS', root_path = CFG_FS.getsyspath( '/' ), settings_files = [ CONFIG_FILE, SETTINGS_FILE ], merge_enabled=True )
CACHE: Dynaconf = Dynaconf( root_path = CFG_FS.getsyspath( '/' ), settings_files = [ CACHE_FILE ] )
SESSIONS: Dynaconf = Dynaconf( root_path = CFG_FS.getsyspath( '/' ), settings_files = [ SESSIONS_FILE ] )

# logging setup

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
class ApplicationContext:

	config: Dynaconf = field( default=SETTINGS )
	sessions: SynoSessions = field( factory=SynoSessions )
	cache: Cache = field( default=None )

	service: WebService = field( default=None )

	__kwargs__: Dict = field( factory=dict, alias='__kwargs__' )

	def __attrs_post_init__( self ):
		# from dynaconf import inspect_settings
		# from rich.pretty import pprint
		# pprint( inspect_settings( SETTINGS ) )

		self.config.update( **self.__kwargs__ )
		self.__configure_log__()

		try:
			self.sessions = SynoSessions.from_str( CFG_FS.readtext( SESSIONS_FILE, 'UTF-8' ) )
			log.debug( f'read {len( self.sessions.sessions)} sessions file from {CFG_FS.getsyspath( SESSIONS_FILE )}' )
		except ResourceNotFound:
			log.error( f'unable to read sessions file from {CFG_FS.getsyspath( SESSIONS_FILE )}' )

		self.cache = Cache( source=CACHE )

	def __configure_log__( self ):
		global DEFAULT_HANDLER, VERBOSE_HANDLER, DEBUG_HANDLER
		if self.config.debug:
			DEBUG_HANDLER.setLevel( DEBUG )
			VERBOSE_HANDLER.setLevel( DISABLE )
			DEFAULT_HANDLER.setLevel( DISABLE )
			log.setLevel( DEBUG )
		elif self.config.verbose:
			DEBUG_HANDLER.setLevel( DISABLE )
			VERBOSE_HANDLER.setLevel( INFO )
			DEFAULT_HANDLER.setLevel( DISABLE )
			log.setLevel( INFO )
		else:
			DEBUG_HANDLER.setLevel( DISABLE )
			VERBOSE_HANDLER.setLevel( DISABLE )
			DEFAULT_HANDLER.setLevel( WARNING )
			log.setLevel( WARNING )

	def save_config_files( self ):
			try:
				CFG_FS.writetext( CACHE_FILE, dump_cache( self.cache ), 'UTF-8' )
			except ResourceNotFound:
				log.error( f'unable to write file {CACHE_FILE}', exc_info=True )

			try:
				CFG_FS.writetext( SESSIONS_FILE, self.sessions.as_str(), 'UTF-8' )
			except ResourceNotFound:
				log.error( f'unable to write sessions file {SESSIONS_FILE}', exc_info=True )

	@property
	def profile( self ) -> Optional[Profile]:
		try:
			p = self.config.profiles[self.config.profile]
			return Profile( url=p.url, account=p.account, password=p.password )
		except BoxKeyError:
			return None

	@property
	def url( self ) -> str:
		return self.config.profiles[self.config.profile].url

	@property
	def account( self ) -> str:
		return self.config.profiles[self.config.profile].account

	@property
	def password( self ) -> str:
		return self.config.profiles[self.config.profile].password

	@property
	def session( self ) -> SynoSession:
		return self.sessions.get( self.config.profile )

def teardown():
	ctx: ApplicationContext = get_current_context().obj
	ctx.sessions[ctx.config.profile] = ctx.service.session
	ctx.save_config_files()
