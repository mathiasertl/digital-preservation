"""
This module is designed for simple option parsing. An L{options.options} instance
instantiated upon import similary to a factory method.
"""

import sys
from optparse import *

class options( object ):
	"""Class responsible for option parsing."""

	instance = None

	def __init__( self ):
		"""
		Parse command-line options. Note that this method implicitly
		gets called if the module is imported for the first time.
		"""

		parser = OptionParser()
		parser.add_option( '--database-backend', metavar="sqlite3",
			default="sqlite3", help="""Choose your database backend. For now, the only available backend is sqlite3.""" )
		parser.add_option( '--max-depth', metavar="N", default=3, type="int",
			help="Choose the maximum recursion depth while crawling the web (default: %default)" )
		parser.add_option( '--detector-backend', default="file", metavar="[file|fits]",
			help="""Choose your file format detector backend (default: %default). """
				"""If you choose 'fits', you must also set the FITS_PATH environment variable.""" )

		# sqlite options:
		sqlite_group = OptionGroup( parser, "SQLite3 options" )
		sqlite_group.add_option( '--database', metavar="PATH", 
			default="test.sqlite3",
			help="Path to SQLite3 database." )
		sqlite_group.add_option( '--cache-size', metavar='N', type="int", default=1000,
			help="Edit size of in-memory cache size for already fetched URLs (default: %default)" )
		parser.add_option_group( sqlite_group )

		self.opts, self.args = parser.parse_args()

	def get( self, option ):
		"""
		Allows you to get an the value of a simple option string.

		@raise RuntimeError: If an unknown option is requested.
		"""

		if hasattr( self.opts, option ):
			return getattr( self.opts, option )
		raise RuntimeError( "%s: unknown option."%(option) )

if options.instance == None:
	options.instance = options()


def get( option ):
	"""
	Shortcut for L{options.options.get}.
	"""
	return options.instance.get( option )

