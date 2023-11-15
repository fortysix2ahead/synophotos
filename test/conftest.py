from importlib.resources import path
from pathlib import Path

from attrs import define, field
from cattrs.preconf.pyyaml import make_converter
from pytest import fail, fixture

converter = make_converter()

@define
class TestConfig:
	user_id: int = field( default=None )
	group_id: int = field( default=None )
	personal_folder: int = field( default=None )
	shared_folder: int = field( default=None )

@fixture
def testconfig() -> TestConfig:
	with path( 'test', '__init__.py' ) as test_path:
		test_config_path = Path( test_path.parent, 'testconfig.yaml' )
		if not test_config_path.exists():
			fail( 'error: testconfig.yaml need to be prepared to run test cases' )

		yield converter.loads(test_config_path.read_text( 'UTF-8' ), TestConfig )
