import os, sys, urllib.parse, urllib.request
from techwatch import htmlparser
from techwatch.file import fits, file

class Crawler(object):
	def __init__( self, root, db, maxdepth=10, lvl=0 ):
		print( 'crawler: %s, lvl: %s/%s' % (root, lvl, maxdepth) )
		self.root = urllib.parse.urlparse( root )
		self.db = db
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

	def is_same_url( self, url ):
		if self.root.scheme != url.scheme:
			return False
		if self.root.netloc != url.netloc:
			return False
		if self.root.path != url.path:
			return False
		return True

	def a_handler( self, attrs ):
		if self.lvl == self.maxdepth:
			return

		src = [ x[1] for x in attrs if x[0] == 'href' ]

		# filter "a" elements without a href attribute
		if len( src ) != 1:
			return
		# filter anchor links
		if src[0].startswith( '#' ):
			return

		url = self.handle_target( urllib.parse.urlparse( src[0] ) )
		if not self.is_same_url( url ):
			crawler = Crawler( url.geturl(), self.db, self.maxdepth, self.lvl+1 )
			crawler.crawl()
#		else:
#			print( "%s and %s are the same url"%(self.root.geturl(), url.geturl() ) )

	def img_handler( self, attrs ):
		src = [ x[1] for x in attrs if x[0] == 'src' ][0]
		url = self.handle_target( urllib.parse.urlparse( src ) )
		
		crawler = Crawler( url.geturl(), self.db, self.maxdepth, self.lvl+1 )
		crawler.crawl()

	def crawl( self ):
		if self.lvl > self.maxdepth:
			return
		if self.db.have_it( self.root.geturl() ):
			return

		# fetch data:
		try:
			response = urllib.request.urlopen( self.root.geturl() )
		except urllib.error.URLError as e:
			# this is with unparsable/unfetchable URLs (i.e. mailto)
			# and 404 not found errors
			return
		page = response.read()
		
		# get format and save it
		detector = file.file()
		format = detector.detect( page )
		self.db.add( self.root.geturl(), format )

		# if its html, we crawl it further
		if detector.ishtml():
			print( "Format: " + str( detector.format, 'utf-8' ) )
#			sys.stdout.flush()
			parser = htmlparser.Parser(
				start_handler={'a': self.a_handler},
				startend_handler={'img': self.img_handler} )
			if type( page ) == bytes:
				page = str( page, 'utf-8' ) # TODO: Get encoding
			parser.feed( page )
