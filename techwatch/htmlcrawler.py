"""
Main HTML crawler function.
"""

import os, sys, html, urllib.parse, urllib.request
from techwatch import htmlparser, options
import techwatch.file

class Crawler(object):
	"""
	This object is responsible for crawling a given URL. The crawl method
	automatically launches further instances of this class for URLs found in
	an HTML document.
	"""

	def __init__( self, url, db, maxdepth=3, lvl=0 ):
		"""
		Constructor. The url-string is automatically encoded.

		@param url: The url to crawl
		@type  url: string
		@param  db: The database backend. This object must be threadsafe
			and implement the same methods as
			L{db.sqlite.backend}.
		@param maxdepth: The maximum recursion depth
		@type  maxdepth: int
		@param lvl: The current recursion level
		@type  lvl: int
		"""

		self.url = self.get_url( url )
		self.urlstr = self.url.geturl()
#		print( 'crawler: %s, lvl: %s/%s' % (self.urlstr, lvl, maxdepth) )

		self.db = db
		self.lvl = lvl
		self.maxdepth = maxdepth

	def get_url( self, string ):
		"""
		Safely quote a string that is assumed not to be URL-encoded.
		
		@param string: The URL to quote
		@type  string: string
		"""
		url = urllib.parse.urlparse( string )
		path = url.path
		while path.find( '//' ) >= 0:
			path = path.replace( '//', '/' )

		try:
			path.encode( 'ascii' )
		except UnicodeEncodeError:
			path = urllib.parse.quote( path )

		try:
			url.query.encode( 'ascii' )
			query = url.query
		except UnicodeEncodeError:
			# query string needs special treatment :-(
			query = urllib.parse.parse_qsl( url.query )
			query = urllib.parse.urlencode( query )
		
		return urllib.parse.ParseResult( url.scheme, url.netloc,
			path, url.params, query, None )

	def handle_target( self, url ):
		"""
		This method handles URLs found in a href/src attribute. It
		automatically detects relative links and prepends the
		appropriate information.

		@param url: The URL to handle. This must be a tuple as returned by
			U{urllib.parse.urlparse<http://docs.python.org/dev/py3k/library/urllib.parse.html#urllib.parse.urlparse>}.
		@return:
			U{urllib.parse.ParseResult<http://docs.python.org/dev/py3k/library/urllib.parse.html#urllib.parse.ParseResult>}.
		"""

		scheme = url.scheme
		netloc = url.netloc
		path = url.path
		params = url.params
		query = url.query
		# we leave the fragment out

		if scheme == "":
			scheme = self.url.scheme
		if netloc == "":
			netloc = self.url.netloc

		try:
			url.path.encode( 'ascii' )
		except UnicodeEncodeError:
			path = urllib.parse.quote( path )

		if not path.startswith( '/' ):
			path = os.path.dirname( self.url.path ) + '/' + path
		while path.find( '//' ) >= 0:
			path = path.replace( '//', '/' )

		return urllib.parse.ParseResult( scheme, netloc, path, params, query, None )

	def is_same_url( self, url ):
		"""
		Check if an URL is the same as the URL that this object crawles.

		@param url: The URL to compare. This must be a tuple as returned by
			U{urllib.parse.urlparse<http://docs.python.org/dev/py3k/library/urllib.parse.html#urllib.parse.urlparse>}
		@return: True if URL is the same, False if not.
		"""
		if self.url.scheme != url.scheme:
			return False
		if self.url.netloc != url.netloc:
			return False
		if self.url.path != url.path:
			return False
		return True

	def a_handler( self, attrs ):
		"""
		Handler for "a" HTML tags. If the tag contains a "href"
		attribute, the URL hasn't been crawled before and is not a
		relative link, this method will launch another crawler for it.

		@param attrs: The same attrs as from
			U{handle_starttag<http://docs.python.org/dev/py3k/library/html.parser.html#html.parser.HTMLParser.handle_starttag>}.
		@see:
			U{html.parser<http://docs.python.org/dev/py3k/library/html.parser.html>}
		"""
		if self.lvl == self.maxdepth:
			# already reached maximum recursion depth
			return

		src = [ x[1] for x in attrs if x[0] == 'href' ]
		# filter "a" elements without a href attribute and anchor links
		if len( src ) != 1 or src[0].startswith( '#' ):
			return

		url = self.handle_target( urllib.parse.urlparse( src[0] ) )
		
		# do not crawl link if it violates crawling-policy:
		policy = options.get( 'crawling_policy' )
		if policy == 'same-domain' and url.netloc != self.url.netloc:
			return
		if self.is_same_url( url ):
			return
		if self.db.have_it( url.geturl() ):
			return
		
		crawler = Crawler( url.geturl(), self.db, self.maxdepth, self.lvl+1 )
		crawler.crawl()

	def img_handler( self, attrs ):
		"""
		Handler for "a" HTML tags. If the tag contains a "href"
		attribute, the URL hasn't been crawled before and is not a
		relative link, this method will launch another crawler for it.

		@param attrs: The same attrs as from
			U{handle_startendtag<http://docs.python.org/dev/py3k/library/html.parser.html#html.parser.HTMLParser.handle_startendtag>}.
		@see:
			U{html.parser<http://docs.python.org/dev/py3k/library/html.parser.html>}
		"""
		if self.lvl == self.maxdepth:
			# already reached maximum recursion depth
			return
		src = [ x[1] for x in attrs if x[0] == 'src' ]
		if len(src) != 1:
			# no src attribute
			return

		url = self.handle_target( urllib.parse.urlparse( src[0] ) )
		
		# do not crawl link if it violates crawling-policy:
		policy = options.get( 'crawling_policy' )
		if policy == 'same-domain' and url.netloc != self.url.netloc:
			return

		if not self.db.have_it( url.geturl() ):
			# fetch this url
			crawler = Crawler( url.geturl(), self.db, self.maxdepth, self.lvl+1 )
			crawler.crawl()

	def crawl( self ):
		"""
		Method actually responsible for crawling the URL given in the
		constructor. This method is the main workhorse as it also
		launches the fileformat detector (see L{file}), saves the format
		to the database backend (see L{db}) and launches the HTML parser
		(see L{htmlparser.Parser}) if the fetched URL turns out to be an
		HTML page.
		"""
		# these should already be caught by the link handlers, this is
		# just to be on the safe side
		if self.lvl > self.maxdepth:
			return
		if self.db.have_it( self.urlstr ):
			print( "NOT CRAWL: %s"%(self.url) )
			return

		# fetch data:
		try:
			request = urllib.request.Request( self.urlstr )
			response = urllib.request.urlopen( request, timeout=10 )
#			response = urllib.request.urlopen( self.urlstr, timeout=10 )

			# get encoding/type from header:
			header = response.getheader( 'Content-Type' )
			fields = header.split( ';' )
			charset = [ f.strip()[8:] for f in fields if f.strip().startswith( 'charset=' ) ][0]
		except UnicodeEncodeError as e:
			print( "UnicodeEncodeError: Opening %s failed: %s" %(self.urlstr, e.reason) )
			return
		except urllib.error.HTTPError as e:
			# catch 403/404/... HTTP errors
			print( 'Error %s: "%s": %s'%(e.getcode(), self.urlstr, e.msg) )
			return
		except urllib.error.URLError as e:
			# catch unparsable/unfetchable URLs (i.e. mailto)
			print( 'Error: "%s": %s'%(self.urlstr, e.reason) )
			return
		except IndexError as e:
			# Content-Type header does not have charset field
			charset = 'utf-8'
		except TypeError:
			# no content-type header
			pass

		# get the actual data from response (this is in bytes!)
		page = response.read()

		# get format and save it
		detector_backend = 'techwatch.file.' + options.get( 'detector_backend' )
		backend = __import__( detector_backend, fromlist=[techwatch.file] )
		detector = backend.backend()
		format = detector.detect( page )
		self.db.add( self.urlstr, format )

		# if its html, we crawl it further
		if detector.ishtml():
#			print( "Format: " + str( detector.format, 'utf-8' ) )
			parser = htmlparser.Parser(
				start_handler={'a': self.a_handler},
				startend_handler={'img': self.img_handler} )
			if type( page ) == bytes:
				try:
					page = str( page, charset )
				except UnicodeDecodeError:
					# decoding failed. Cannot parse.
					return
			try:
				parser.feed( page )
			except html.parser.HTMLParseError as e:
				print( "Error: HTML parsing failed for %s: %s"%(self.urlstr, e.msg) )
