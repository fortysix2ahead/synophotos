from __future__ import annotations

from logging import getLogger
from re import compile as rx_compile
from typing import Dict

from attrs import define, field
from exif import Image

rx_lat_lon = rx_compile( r'(\d+)deg (\d+)\' (\d+)\"' )

log = getLogger( __name__ )

@define
class SynoExif:

	data: Dict = field( factory=dict )

	@property
	def city( self ):
		return self.data.get( 'City' ) # sample value: 'Berlin'

	@property
	def country( self ):
		return self.data.get( 'Country' ) # sample value: 'Germany'

	@property
	def country_code( self ):
		return self.data.get( 'Country Code' ) # sample value: 'DEU'

	@property
	def country_name( self ):
		return self.data.get( 'Country Name' ) # sample value: 'Germany'

	@property
	def create_date( self ):
		return self.data.get( 'Create Date' ) # sample value: '2022-01-30T16:50:46'

	@property
	def date_and_time( self ):
		return self.data.get( 'Date and Time' ) # sample value: '2022:01:30 16:50:46', in addition there's 'Date and Time (digitized)' and '(original)'

	@property
	def image_description( self ):
		return self.data.get( 'Image Description' )

	@property
	def gps_altitude( self ):
		return self.data.get( 'GPS Altitude' ) # sample value '200 m'

	@property
	def gps_altitude_ref( self ):
		return self.data.get( 'GPS Altitude Reference' ) # sample value 'Above sea level'

	@property
	def gps_latitude( self ):
		return self.data.get( 'GPS Latitude' ) # sample value: "55deg 32' 60""

	@property
	def gps_latitude_ref( self ):
		return self.data.get( 'GPS Latitude Reference' ) # sample value: 'North'

	@property
	def gps_longitude( self ):
		return self.data.get( 'GPS Longitude' ) # sample value: "8deg 53' 17""

	@property
	def gps_longitude_ref( self ):
		return self.data.get( 'GPS Longitude Reference' ) # sample value: 'East'

	@property
	def location( self ):
		return self.data.get( 'Location' ) # sample value: 'Zoologischer Garten'

	@property
	def location_code( self ):
		return self.data.get( 'Location Code' ) # sample value: 'DE'

	@property
	def location_name( self ):
		return self.data.get( 'Location Name' ) # sample value: 'Zoologischer Garten'

	@property
	def metadata_date( self ):
		return self.data.get( 'Metadata Date' )

	@property
	def modify_date( self ):
		return self.data.get( 'Modify Date' ) # sample value: '2023-11-16T14:45:06'

	@property
	def offset_time( self ):
		return self.data.get( 'Offset Time' ) # sample value: '+01:00', in addition there's 'Offset Time Original'

	@property
	def province_state( self ):
		return self.data.get( 'Province State' ) # sample value: 'Brandenburg'

	@property
	def state( self ):
		return self.data.get( 'State' )  # sample value: 'Brandenburg'

	@property
	def subject( self ):
		return self.data.get( 'Subject' ) # title of the image?

	@property
	def sub_location( self ):
		return self.data.get( 'Sub Location' ) # sample value: 'Zoologischer Garten'

	def set( self, img: Image, attribute, value ):
		if value is not None:
			img.set( attribute, value )

	def set_gps_data( self, img, item ):
		lat, lon, lat_ref, lon_ref = None, None, None, None
		try:
			if match := rx_lat_lon.fullmatch( self.gps_latitude ):
				lat = tuple( float( v ) for v in match.groups() )
			if match := rx_lat_lon.fullmatch( self.gps_longitude ):
				lon = tuple( float( v ) for v in match.groups() )
			if self.gps_latitude_ref and self.gps_longitude_ref:
				lat_ref = 'N' if self.gps_latitude_ref == 'North' else 'S'
				lon_ref = 'E' if self.gps_longitude_ref == 'East' else 'W'
		except TypeError: # catch cases when no gps data exists
			pass

		if lat and lon and lat_ref and lon_ref:
			self.set( img, 'gps_latitude', lat )
			self.set( img, 'gps_longitude', lon )
			self.set( img, 'gps_latitude_ref', lat_ref )
			self.set( img, 'gps_longitude_ref', lon_ref )
			log.info( f'setting GPS data for {item.filename} \[id {item.id}] to {lat} {lat_ref} / {lon} {lon_ref}' )
		else:
			log.info( f'unable to set GPS data for {item.filename} (id {item.id}) (no valid data available)' )

	# todo: location data CANNOT be saved in EXIF, IPTC/XMP must be used instead
	def set_location_data( self, img ):
		pass

	def apply( self, content: bytes, item ) -> bytes:

		# analysis:
		# item.indexed: time the image was initially (?) indexed by Synology Photos (changing image metadata and triggering a re-index does not change this time!)
		# item.modified: time that can be inserted manually via web interface: (i) -> Information -> Time
		# item.additional.description: description which can be set via web interface
		# item.additional.thumbnail.cache_key: seems to <id>_<timestamp>, unclear what timestamp means, maybe time of thumbnail creation
		# exif.create_date: exif creation date (seems to remain untouched)
		# exif.modify_date: exif modification date (seems to remain untouched)
		# exif.metadata_date: sameas modify date -> unclear what this date is
		# exif.date_and_time: modification date from above (item.modified)
		# exif.image_description: same description as above

		img = Image( content )

		# all attributes at https://exif.readthedocs.io/en/latest/api_reference.html#image-attributes
		# information on formats: https://en.wikipedia.org/wiki/Exif

		# title / description
		self.set( img, 'image_description', self.image_description )

		# date and time, format: YYYY:MM:DD hh:mm:ss
		self.set( img, 'datetime', self.date_and_time )
		self.set( img, 'datetime_digitized', self.date_and_time )
		self.set( img, 'datetime_original', self.date_and_time )

		# time zone offset
		if self.offset_time:
			self.set( img, 'offset_time', self.offset_time )
			self.set( img, 'offset_time_digitized', self.offset_time )
			self.set( img, 'offset_time_original', self.offset_time )

		log.info( f'setting time data for {item.filename} \[id {item.id}] to {self.date_and_time}, offset {self.offset_time}' )

		# GPS data
		self.set_gps_data( img, item )

		# location data
		self.set_location_data( img )

		return img.get_file()
