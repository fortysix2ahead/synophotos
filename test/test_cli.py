from typing import List

from attrs import define, field
from click.testing import CliRunner

from synophotos import __version__
from synophotos.cli import cli

@define
class Invocation:

	code: int = field()
	out: List[str] = field()
	err: List[str] = field()

	# certain line equals tern

	def assert_err_line_is( self, term: str, line_no: int ):
		assert len( self.err ) >= line_no + 1
		assert self.err[line_no] == term

	def assert_out_line_is( self, term: str, line_no: int = 0 ):
		assert len( self.out ) >= line_no + 1
		assert self.out[line_no] == term

	def assert_term_in_err_line( self, term: str, line_no: int ):
		assert self.err and len( self.err ) > line_no + 1
		assert term in self.err[line_no]

	def assert_term_in_stdout( self, term ):
		assert len( self.out ) > 0 and any( term in l for l in self.out )

# predefined commands

cmd_nocmd = ''
cmd_version = 'version'

# no command

def test_nocommand( testconfig ):
	invoke( cmd_nocmd )

# version

def test_version():
	invoke( cmd_version ).assert_out_line_is( __version__ )

def invoke( cmdline: str ) -> Invocation:
	runner = CliRunner( mix_stderr=False )
	result = runner.invoke( cli, cmdline, catch_exceptions=False )
	print( result.exc_info )
	return Invocation( result.exit_code, result.stdout.splitlines(), result.stderr.splitlines() )
