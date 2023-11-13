from abc import abstractmethod
from datetime import datetime, timedelta
from logging import getLogger
from sys import exit as sysexit
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from attrs import define, field
from cattrs import Converter
from requests import JSONDecodeError, PreparedRequest, Response, get, post
from rich.pretty import pretty_repr
from rich.prompt import Prompt
from typing_extensions import Protocol

from synophotos.error_codes import CODE_SUCCESS, CODE_UNKNOWN, error_codes
from synophotos.parameters.photos import SID
from synophotos.parameters.webservice import ENTRY_URL, LOGIN_PARAMS
from synophotos.ui import print_error

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

	def __attrs_post_init__( self ):
		self.status_code = self.response.status_code
		try:
			json = self.response.json()
			self.success = json.get( 'success', False )
			if self.success:
				self.data = json.get( 'data', { } )
			else:
				self.error_code = json.get( 'error' ).get( 'code' )
				self.error_msg = error_codes.get( self.error_code, error_codes.get( CODE_UNKNOWN ) )
		except JSONDecodeError:
			self.success = False

	def as_bytes( self ) -> bytes:
		return self.response.content

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
class SynoWebService:
	url: str = field( default=None )
	account: str = field( default=None )
	password: str = field( default=None )

	session: SynoSession = field( default=None )

	@property
	def session_id( self ) -> Optional[str]:
		return self.session.sid if self.session else None

	@property
	def device_id( self ) -> Optional[str]:
		return self.session.device_id if self.session else None

	def entry( self, payload: Dict, **kwargs ) -> SynoResponse:
		return self.get( ENTRY_URL, payload, **kwargs )

	def req( self, fn: Callable, url: str, template: Dict, **kwargs ) -> SynoResponse:
		url = self.get_url( url )
		if self.session_id:
			template = template | SID | { '_sid': self.session_id }

		params = template | kwargs  # create variable making debugging easier

		log.debug( f'[dark_orange]{fn.__name__.upper()}[/dark_orange] {url}' )
		log.debug( f'[dark_orange]Parameters:[/dark_orange] {pretty_repr( params )}' )

		response: Response = fn( url=url, params=params, verify=True )

		log.debug( f'[dark_orange]Response:[/dark_orange] {response.status_code}' )
		try:
			log.debug( f'[dark_orange]Payload:[/dark_orange] {pretty_repr( response.json(), max_depth=6 )}' )
		except JSONDecodeError:
			log.debug( f'[dark_orange]Payload:[/dark_orange] <binary> length={len( response.content )}' )

		return SynoResponse( response=response )

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

		save_session = True  # todo: make this configurable?
		#if save_session:
		#	ctx.config.sessions[ctx.config.config.profile] = self.session
		#	ctx.config.save_sessions()

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
