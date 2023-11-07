from abc import abstractmethod
from datetime import datetime, timedelta
from logging import getLogger
from sys import exit as sysexit
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar

from attrs import define, field
from requests import get, JSONDecodeError, post, PreparedRequest, Response
from rich.pretty import pretty_repr
from rich.prompt import Prompt
from typing_extensions import Protocol

from synophotos.error_codes import CODE_SUCCESS, CODE_UNKNOWN, error_codes
from synophotos.parameters.webservice import ENTRY_URL, LOGIN_PARAMS

log = getLogger( __name__ )

T = TypeVar( 'T' )

SESSION_TIMEOUT = timedelta( days=30 )

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

	factory: ClassVar = field( default=None )

	response: Response = field( default=None )
	status_code: int = field( default=None )
	data: Dict = field( factory=dict )
	success: bool = field( default=False )
	error_code: int = field( default=None )
	error_msg: str = field( default=None )


	def __post_init__( self ):
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

	def as_list( self, cls: Type[T] ) -> List[T]:
		if element_list := self.data.get( 'list' ):
			return sorted( [SynoResponse.factory.load( e, cls ) for e in element_list], key=lambda e: e.id )
		else:
			return []

	def as_obj( self, cls: Type[T] ) -> T:
		first_key, first_value = next( iter( self.data.items() ) )
		return SynoResponse.factory.load( first_value, cls )

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

	updated_at: Optional[datetime] = field( default=None )

	def is_valid( self ) -> bool:
		if self.error_code == CODE_SUCCESS:
			if self.updated_at and ( datetime.utcnow() - self.updated_at < SESSION_TIMEOUT ):
				return True
		return False

	def as_dict( self ) -> Dict:
		return FACTORY.dump( self, SynoSession )

@define
class SynoWebService:
	url: str = field( default=None )
	account: str = field( default=None )
	password: str = field( default=None )

	session: SynoSession = field( default=None )

	def __post_init__( self ):
		self._factory = Factory()

	@property
	def session_id( self ) -> Optional[str]:
		return self.session.sid if self.session else None

	@property
	def device_id( self ) -> Optional[str]:
		return self.session.device_id if self.session else None

	def get( self, url: str, template: Dict, **kwargs ) -> SynoResponse:
		if self.session_id:
			template = { **template, '_sid': self.session_id }

		params = { **template, **kwargs }  # create variable making debuggin easier

		log.debug( f'GET {self.get_url( url )}, parameters:' )
		log.debug( pretty_repr( params ) )

		response = get(
			url=self.get_url( url ),
			params=params,
			verify=True
		)

		log.debug( f'Received response with status = {response.status_code}, and payload:' )
		log.debug( pretty_repr( response.json(), max_depth=2 ) )

		return SynoResponse( response=response )

	def post( self, url: str, template: Dict, **kwargs ) -> SynoResponse:
		if self.session_id:
			template = { **template, '_sid': self.session_id }

		log.debug( f'POST {self.get_url( url )}, parameters:' )
		log.debug( pretty_repr( { **template, **kwargs } ) )

		response = post(
			url=self.get_url( url ),
			params={ **template, **kwargs },
			verify=True
		)

		log.debug( f'Received response with status = {response.status_code}, and payload:' )
		log.debug( pretty_repr( response.json(), max_depth=2 ) )

		return SynoResponse( response )

	def get_url( self, stub: str ) -> str:
		return stub.format( url=self.url )

	def login( self, ctx, otp_code: str = None ) -> SynoSession:
		# todo: check if saved session has been expired, but unclear how to detect that
		if self.session and self.session.is_valid():
			log.debug( f'reusing session with SID = {self.session.sid}, created at {self.session.updated_at}' )
			return self.session

		self.session = self._login()
		if not self.session.is_valid():
			if self.session.error_code == 403:  # 2FA requested
				otp_token = Prompt.ask( 'Service responded with HTTP 403, 2FA seems to be enabled, please enter 2FA code' )
				self.session = self._login( otp_token )
				if not self.session.is_valid():
					ctx.console.print( f'error logging in: code={self.session.error_code}, msg={self.session.error_msg}' )
					sysexit( -1 )
				else:
					log.debug( f'created new session with SID = {self.session.sid}' )
			else:
				ctx.console.print( f'error logging in: code={self.session.error_code}, msg={self.session.error_msg}' )
				sysexit( -1 )

		save_session = True  # todo: make this configurable?
		if save_session:
			ctx.cfg.sessions[ctx.cfg.config.profile] = self.session
			ctx.cfg.save_sessions()

		return self.session

	def _login( self, otp_code: str = None ) -> SynoSession:
		if otp_code:
			syno_response = self.get( ENTRY_URL, LOGIN_PARAMS, account=self.account, passwd=self.password, otp_code=otp_code )
		else:
			syno_response = self.get( ENTRY_URL, LOGIN_PARAMS, account=self.account, passwd=self.password )

		if syno_response.success:
			session = FACTORY.load( syno_response.data, SynoSession )
			session.updated_at = datetime.utcnow()
			return session
		else:
			return SynoSession( error_code=syno_response.error_code, error_msg=syno_response.error_msg )
