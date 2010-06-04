from html.parser import HTMLParser

class Parser( HTMLParser ):
	def __init__( self, start_handler={}, startend_handler={}, end_handler={} ):
		HTMLParser.__init__( self )
		self.start_handler = start_handler # <a ...>
		self.startend_handler = startend_handler # <img .../>
		self.end_handler = end_handler # </a>

	def handle_starttag( self, tag, attrs ):
		if tag in self.start_handler.keys():
			self.start_handler[tag]( attrs )

	def handle_startendtag( self, tag, attrs ):
		if tag in self.startend_handler.keys():
			self.startend_handler[tag]( attrs )

	def handle_endtag( self, tag ):
		if tag in self.end_handler.keys():
			self.end_handler[tag]()
