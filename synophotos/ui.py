from dataclasses import fields
from typing import Any, List, Optional, Type

from attrs import fields
from attrs.exceptions import NotAnAttrsClassError

from rich import box
from rich.console import Console
from rich.pretty import Pretty, pretty_repr
from rich.prompt import Confirm
from rich.style import Style
from rich.table import Table

cs = Console()

blue = Style( color='blue' )

def confirm( msg: str, force: bool = False ) -> bool:
	return force or Confirm().ask( msg )

def pprint( item: Any ):
	cs.print( item )

def print_obj_table( obj: Any ):
	cs.print( obj_table( obj ) )

def print_obj( obj: Any ) -> None:
		if isinstance( obj, list ):
			pprint( dataclass_table( obj ) )
		else:
			pprint( obj )

def print_error( msg: str ):
	cs.print( f'[red]Error:[/red] {msg}' )

#

def obj_table( obj: Any ) -> Table:
	table = Table( box=box.MINIMAL, show_header=True, show_footer=False )
	[ table.add_column( c, header_style=blue ) for c in ['attribute', 'value'] ]

	try:
		attributes = sorted( fields( obj.__class__ ), key=lambda f: f.name )

		# append additional to the end of the list
		if additional := next( iter( [ a for a in attributes if a.name == 'additional' ] ), None ):
			attributes.remove( additional )
			attributes.append( additional )

		for a in attributes:
			table.add_row( Pretty( a.name ), Pretty( getattr( obj, a.name ) ) )
	except NotAnAttrsClassError:
		pass

	return table

def table_for( cols: List, rows: List[List] ) -> Table:
	table = Table( box=box.MINIMAL, show_header=True, show_footer=False )
	[ table.add_column( c, header_style=blue ) for c in cols ]
	for row in rows:
		table.add_row( *[Pretty( r ) for r in row] )
		# table.add_row( *[pretty_repr( r ) for r in row] )
	return table

def dataclass_table( instances: List, cls: Type = None ) -> Optional[Table]:
	# determine fields to display

	try:
		# noinspection PyUnresolvedReferences
		table_fields: List[str] = cls.table_fields()
	except AttributeError:
		try:
			table_fields = instances[0].__class__.table_fields()
		except (AttributeError, IndexError):
			try:
				table_fields = [f.name for f in fields( instances[0] )]
			except (TypeError, IndexError):
				try:
					table_fields = [f for f in instances[0].keys()]
				except (AttributeError, IndexError):
					table_fields: List[str] = []

	# determine values to display

	rows = []
	for i in instances:
		try:
			values = [getattr( i, f ) for f in table_fields]
		except AttributeError:
			try:
				values = [i.get( f ) for f in table_fields]
			except KeyError:
				values = ['n/a' for f in table_fields]
		rows.append( values )

	# create table

	table = Table( box=box.MINIMAL, show_header=True, show_footer=False )

	for f in table_fields:
		table.add_column( f, header_style=blue )

	for row in rows:
		table.add_row( *[Pretty( v ) for v in row] )

	return table
