#!/usr/bin/python3

import os
from techwatch import *
from techwatch.db import sqlite

os.remove( './test.db' )
db = sqlite.backend( './test.db' )

path = "http://tubasis.at/~mati/test.html"
crawler = htmlcrawler.Crawler( path, db, 3 )
crawler.crawl()

db.queue.join( )

#page = open( path ).read()
#if type( page ) == type( bytes ):
#	page = str( page, 'utf-8' ) # TODO: Get encoding
#parser.feed( page )
