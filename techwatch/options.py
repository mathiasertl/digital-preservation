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
		parser.add_option( '--from', default="e0326788@student.tuwien.ac.at", 
			metavar="user@example.com",
			help="Default sender of notification mails (Default: %default)." )
		parser.add_option( '--to', default="e0326788@student.tuwien.ac.at",
			metavar="user@example.com",
			help="Default recipient of notifications." )
		parser.add_option( '--smtp-server', default="mr.tuwien.ac.at",
			help="Default SMTP relay (default: %default). See README.txt for help." )
		parser.add_option( '--threshold', default=10.0, type='float',
			help="Send an error if a fileformat is below the specified threshold (default: %default)" )
		parser.add_option( '--seed', default='http://vowi.fsinf.at', metavar='URL',
			help="The URL where to start crawling (default: %default)" )
		parser.add_option( '--policy', type="choice", choices=["all", "same-domain"],
			default="same-domain", dest="crawling_policy", metavar='[all|same-domain]',
			help="Choose on which policy to follow links: Either follow 'all' links or stay on the same domain (default: %default)" )

		# sqlite options:
		sqlite_group = OptionGroup( parser, "SQLite3 options" )
		sqlite_group.add_option( '--database', metavar="PATH", 
			default="db.sqlite3",
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

