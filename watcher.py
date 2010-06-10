#!/usr/bin/python3

import os
from techwatch import *
from techwatch.db import sqlite

db_path = options.get( 'database' )
if os.path.exists( db_path ):
	os.remove( db_path )
db = sqlite.backend( db_path )
recursion_depth = options.get( 'max_depth' )

path = "http://vowi.fsinf.at"
#path = "http://www.gnu.org/copyleft/fdl.html"
#path = "http://tubasis.at/~mati/test.html"
#path = "http://vowi.fsinf.at/wiki?title=FAQ Abkürzungen&oldid=49098"
crawler = htmlcrawler.Crawler( path, db, recursion_depth )
crawler.crawl()

db.queue.join( )
