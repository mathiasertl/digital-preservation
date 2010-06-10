#!/usr/bin/python3

import os
from techwatch import *
from techwatch.db import sqlite

db_path = options.get( 'database' )
if os.path.exists( db_path ):
	os.remove( db_path )
db = sqlite.backend( db_path )
recursion_depth = options.get( 'max_depth' )

path = options.get( 'seed' )
crawler = htmlcrawler.Crawler( path, db, recursion_depth )
crawler.crawl()

# waiting for crawl to complete:
db.queue.join( )

# find rare formats:
rare_formats = []
for format in db.formats():
	percentage = db.percentage( format )
	if percentage < options.get( 'threshold' ):
		rare_formats.append( (format, percentage) )

# send mail if one or more fileformats are rare:
if len(rare_formats) > 0:
	msg = """The following formats seem to be rare and are below the threshold of %s
percent:

"""%(options.get( 'threshold' ) )
	for format in rare_formats:
		msg += ( "* %s: %.3f percent\n"%(str(format[0], 'utf-8'), format[1]) )

	msg += "\nPlease make a note of it."
	mail.send( msg )
