from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timedelta
from logging import getLogger
from sys import exit as sysexit
from typing import Any, Callable, ClassVar, Dict, List, Optional, Type, TypeVar

from attrs import define, field
from cattrs import Converter
from cattrs.preconf.pyyaml import make_converter
from requests import JSONDecodeError, PreparedRequest, Response, get, post
from rich.pretty import pretty_repr
from rich.prompt import Prompt
from typing_extensions import Protocol

from synophotos import Cache
from synophotos.error_codes import CODE_SUCCESS, CODE_UNKNOWN, error_codes
from synophotos.parameters.photos import SID
from synophotos.parameters.webservice import ENTRY_URL, LOGIN_PARAMS, LOGIN_MFA
from synophotos.ui import print_error
from synophotos.utils import lower_keys

log = getLogger( __name__ )

T = TypeVar( 'T' )
SESSION_TIMEOUT = timedelta( days=30 )

conv = Converter()

class WebService( Protocol ):

	@property
	def url( self ) -> Optional[str]:
		return None

	@url.setter
	def url( self, url: str ) -> None:
		pass

	@abstractmethod
	def get_url( self, url_stub: str ) -> str:
		pass

@define
class SynoRequest:
	pass

@define
class SynoResponse:

	response: Response = field( default=None )
	status_code: int = field( default=None )
	data: Dict = field( factory=dict )
	success: bool = field( default=False )
	error_code: int = field( default=None )
	error_msg: str = field( default=None )

	# noinspection PyTestUnpassedFixture
	def __attrs_post_init__( self ):
		self.status_code = self.response.status_code
		try:
			json = self.response.json()
			self.success = json.get( 'success', False )
			if self.success:
				self.data = json.get( 'data', {} )
				self.error_code = CODE_SUCCESS
				self.error_msg = error_codes.get( CODE_SUCCESS )
			else:
				self.error_code = json.get( 'error' ).get( 'code' )
				self.error_msg = error_codes.get( self.error_code, error_codes.get( CODE_UNKNOWN ) )
		except JSONDecodeError:
			self.success = True if self.status_code in range( 200, 300 ) else False

	@property
	def method( self ) -> str:
		return self.response.request.method

	@property
	def path_url( self ) -> str:
		return self.response.request.path_url

	@property
	def short_url( self ) -> str:
		return self.response.request.path_url.split( '&' )[0]

	@property
	def url( self ) -> str:
		return self.response.request.url

	@property
	def mfa_requested( self ) -> bool:
		return self.error_code == 403

	@property
	def mfa_token( self ) -> str:
		return self.error_code == 403

	@property
	def unauthorized( self ) -> bool:
		return not self.success and self.error_code == 119

	def as_bytes( self ) -> bytes:
		return self.response.content

	def as_text( self ) -> str:
		return self.response.text

	def as_json( self ) -> Dict:
		try:
			return self.response.json()
		except JSONDecodeError:
			return {}

	@property
	def otp_token( self ) -> str:
		return self.as_json().get( 'error', {} ).get( 'errors', {} ).get( 'token' )

	def as_list( self, cls: Type[T] ) -> List[T]:
		return [conv.structure( e, cls ) for e in self.as_dict_list()]

	def as_dict_list( self ) -> List[Dict]:
		if element_list := self.data.get( 'list' ):
			return sorted( [e for e in element_list], key=lambda e: e.get( 'id' ) )
		else:
			return []

	def as_obj( self, cls: Type[T] ) -> T:
		return conv.structure( next( iter( self.data.values() ) ), cls )

		# todo: put check of data type in here?
		# key, value = next( iter( self.data.items() ) )
		# if list( self.data.keys() ) == [ 'list' ]:
		# 	return [ conv.structure( i, cls ) for i in value ]
		# else:
		#	  return conv.structure( value, cls )

	def request( self ) -> PreparedRequest:
		return self.response.request

	def response_data( self, key: str ) -> Any:
		return self.data.get( key, None )

@define
class SynoSession:

	account: str = field( default=None )
	device_id: str = field( default=None )
	ik_message: str = field( default=None )
	is_portal_port: bool = field( default=None )
	sid: str = field( default=None )
	synotoken: str = field( default=None )

	error_code: int = field( default=CODE_SUCCESS )
	error_msg: Optional[str] = field( default=None )

	updated_at: Optional[str] = field( default=None )

	@property
	def updated( self ) -> datetime:
		return datetime.fromisoformat( self.updated_at )

	def is_valid( self ) -> bool:
		if self.error_code == CODE_SUCCESS:
			if self.updated_at and ( datetime.utcnow() - self.updated < SESSION_TIMEOUT ):
				return True
		return False

@define
class SynoSessions:

	# cattrs converter
	converter: ClassVar[Converter] = make_converter( omit_if_default=True )

	# fields
	sessions: Dict[str, SynoSession] = field( factory=dict )

	@classmethod
	def from_dict( cls, d: Dict ) -> SynoSessions:
		return SynoSessions( sessions=SynoSessions.converter.structure( lower_keys( d ), Dict[str, SynoSession] ) )

	@classmethod
	def from_str( cls, s: str ) -> SynoSessions:
		return SynoSessions( sessions=SynoSessions.converter.loads( s, Dict[str, SynoSession] ) )

	def __getitem__( self, item ) -> Optional[SynoSession]:
		return self.sessions.get( item )

	def __setitem__( self, key: str, value: SynoSession ) -> None:
		self.sessions[key] = value

	def get( self, name: str ) -> Optional[SynoSession]:
		return self[name]

	def as_dict( self ) -> Dict:
		return SynoSessions.converter.unstructure( self.sessions, Dict[str, SynoSession] )

	def as_str( self ) -> str:
		return SynoSessions.converter.dumps( self.sessions, Dict[str, SynoSession] )

@define
class SynoWebService:
	url: str = field( default=None )
	account: str = field( default=None )
	password: str = field( default=None )

	session: SynoSession = field( default=None )
	cache: Cache = field( default=None )

	@property
	def session_id( self ) -> Optional[str]:
		return self.session.sid if self.session else None

	@property
	def device_id( self ) -> Optional[str]:
		return self.session.device_id if self.session else None

	def enable_cache( self, cache: Cache ) -> None:
		self.cache = cache if cache else Cache()
		self.cache.enabled = True

	def entry( self, payload: Dict, **kwargs ) -> SynoResponse:
		return self.get( ENTRY_URL, payload, **kwargs )

	def req( self, fn: Callable, url: str, template: Dict, attempt_login: bool = True, **kwargs ) -> SynoResponse:
		url = self.get_url( url )
		if self.session_id:
			template = template | SID | { '_sid': self.session_id }

		params = template | kwargs  # create variable making debugging easier
		params = { k: v for k, v in params.items() if v is not None } # throw away all None values

		_log_request( fn, url, params )

		# try to send request
		response = SynoResponse( response=fn( url=url, params=params, verify=True ) )
		_log_response( response )

		# when not authenticated, Synology answers with error code 119, so attempt to login and retry
		if attempt_login and response.unauthorized:
			log.info( f'session for user [green]{self.account}[/green] seems be outdated or does not exist, attempting to login' )

			login_params = LOGIN_PARAMS | { 'account': self.account, 'passwd': self.password }
			login_response = self.req( get, url, LOGIN_PARAMS, attempt_login=False, **login_params ) # set attempt_login=False to prevent endless loop!
			# do not log this request as it will be logged when calling req()
			# _log_response( login_response )

			# login failed again
			if login_response.success:
				log.info( f'login for user [green]{self.account}[/green] successful' )
			else:
				if login_response.mfa_requested:
					log.info( f'login for user [green]{self.account}[/green] failed, 2FA seems to be enabled' )
					otp_code = Prompt.ask( 'Multi-factor authentication seems to be enabled, please enter code' )
					login_params = login_params | { 'passwd': login_response.otp_token, 'otp_code': otp_code }
					login_response = self.req( get, url, LOGIN_MFA, attempt_login=False, **login_params )  # set attempt_login=False to prevent endless loop!

				# login finally failed, give up
				if not login_response.success:
					print_error( f'login for user [green]{self.account}[/green] failed, giving up ...' )
					return login_response

			# update parameters with sid and try again
			params = params | SID | { '_sid': login_response.data.get( 'sid' ) }
			retry_response = SynoResponse( response=fn( url=url, params=params, verify=True ) )
			_log_response( retry_response )
			return retry_response

		return response

	def get( self, url: str, template: Dict, **kwargs ) -> SynoResponse:
		return self.req( get, url, template, **kwargs )

	def post( self, url: str, template: Dict, **kwargs ) -> SynoResponse:
		return self.req( post, url, template, **kwargs )

	def get_url( self, stub: str ) -> str:
		return stub.format( url=self.url )

	def login( self, ctx, otp_code: str = None ) -> SynoSession:
		# todo: check if saved session has been expired, but unclear how to detect that
		if self.session and self.session.is_valid():
			log.info( f'reusing session with SID = {self.session.sid}, created at {self.session.updated_at}' )
			return self.session

		self.session = self._login()
		if not self.session.is_valid():
			if self.session.error_code == 403:  # 2FA requested
				otp_token = Prompt.ask( 'Service responded with HTTP 403, 2FA seems to be enabled, please enter 2FA code' )
				self.session = self._login( otp_token )
				if not self.session.is_valid():
					print_error( f'unable to log in: code={self.session.error_code}, msg={self.session.error_msg}' )
					sysexit( -1 )
				else:
					log.info( f'created new session with SID = {self.session.sid}' )
			else:
				print_error( f'unable to log in: code={self.session.error_code}, msg={self.session.error_msg}' )
				sysexit( -1 )

		ctx.sessions[ctx.config.profile] = self.session
		return self.session

	def _login( self, otp_code: str = None ) -> SynoSession:
		if otp_code:
			syno_response = self.get( ENTRY_URL, LOGIN_PARAMS, account=self.account, passwd=self.password, otp_code=otp_code )
		else:
			syno_response = self.get( ENTRY_URL, LOGIN_PARAMS, account=self.account, passwd=self.password )

		if syno_response.success:
			return conv.structure_attrs_fromdict( {**syno_response.data, 'updated_at': datetime.utcnow().isoformat()}, SynoSession )
		else:
			return conv.structure_attrs_fromdict( {'error_code': syno_response.error_code, 'error_msg': syno_response.error_msg}, SynoSession )

# helpers

def _log_request( fn: Callable, url: str, params: Dict ) -> None:
	#log.debug( f'[dark_orange]{fn.__name__.upper()}[/dark_orange] {url}' )
	#log.debug( f'[dark_orange]Parameters:[/dark_orange] {pretty_repr( params )}' )
	log.debug( f'[dark_orange]{fn.__name__.upper()}[/dark_orange] {url}: {pretty_repr( params )}' )

def _log_response( response: SynoResponse ) -> None:
	log.info( f'answer to request [green]{response.method} {response.short_url}[/green]: {response.error_code} - {response.error_msg}' )

	response_str = f'[dark_orange]Response code:[/dark_orange] {response.status_code}'
	try:
		log.debug( f'{response_str}, [dark_orange]payload:[/dark_orange] {pretty_repr( response.response.json(), max_depth=6 )}' )
	except JSONDecodeError:
		log.debug( f'[dark_orange]Payload:[/dark_orange] <binary> length={len( response.response.content )}' )
