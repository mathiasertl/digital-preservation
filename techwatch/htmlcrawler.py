import os, urllib.parse, urllib.request
from techwatch import htmlparser
from techwatch.file import fits

class Crawler(object):
	def __init__( self, root, lvl=0, maxdepth=10 ):
		self.root = urllib.parse.urlparse( root )
		self.lvl = lvl
		self.maxdepth = maxdepth

	def handle_target( self, url ):
		scheme = url.scheme
		netloc = url.netloc
		path = url.path
		params = url.params
		query = url.query
		fragment = url.fragment

		if scheme == "":
			scheme = self.root.scheme
		if netloc == "":
			netloc = self.root.netloc
		if not path.startswith( '/' ):
			path = os.path.dirname( self.root.path ) + '/' + path

		return urllib.parse.ParseResult( scheme, netloc, path, params, query, fragment )

	def a_handler( self, attrs ):
		src = [ x[1] for x in attrs if x[0] == 'href' ][0]
		url = self.handle_target( urllib.parse.urlparse( src ) )
		print( url )

	def img_handler( self, attrs ):
		src = [ x[1] for x in attrs if x[0] == 'src' ][0]
		url = self.handle_target( urllib.parse.urlparse( src ) )
#		print( url )

	def crawl( self ):
		# fetch data:
		page = urllib.request.urlopen( self.root.geturl() ).read()
		
		# get format and save it
		detector = fits.fits()
		format = detector.detect( page )

		# if its html, we crawl it further
		if detector.ishtml():
			parser = htmlparser.Parser(
				start_handler={'a': self.a_handler},
				startend_handler={'img': self.img_handler} )
			if type( page ) == bytes:
				page = str( page, 'utf-8' ) # TODO: Get encoding
			parser.feed( page )
