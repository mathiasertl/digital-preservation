"""
This module implements a simple HTML parser.
"""

from html.parser import HTMLParser

class Parser( HTMLParser ):
	"""
	Rather simple implementation of 
	U{html.parser.HTMLParser<http://docs.python.org/dev/py3k/library/html.parser.html#html.parser.HTMLParser>}.
	See the constructor for more information. See html.parser.HTMLParser for
	documentation on the other methods of this class.
	"""

	def __init__( self, start_handler={}, startend_handler={}, end_handler={} ):
		"""
		The constructor allows you to register handlers for each
		individual start(end)tag. The parameters must be a dictionary
		with the tags as keys and a method as their value.
		"""
		HTMLParser.__init__( self )
		self.start_handler = start_handler # e.g. <a ...>
		self.startend_handler = startend_handler # e.g. <img .../>
		self.end_handler = end_handler # e.g. </a>

	def handle_starttag( self, tag, attrs ):
		if tag in self.start_handler.keys():
			self.start_handler[tag]( attrs )

	def handle_startendtag( self, tag, attrs ):
		if tag in self.startend_handler.keys():
			self.startend_handler[tag]( attrs )

	def handle_endtag( self, tag ):
		if tag in self.end_handler.keys():
			self.end_handler[tag]()
