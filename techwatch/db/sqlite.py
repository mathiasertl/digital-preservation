"""
Database backend using sqlite3.
"""

from techwatch import options
import os, time, sqlite3, queue
from threading import Thread

class backend(object):
	"""
	A database backend using SQLite3. SQLite3 is fast, simple, easy to set
	up and above all, integrated into python. The class uses a Queue to
	implement thread-safety. The backend uses a small cache for URLs that
	are already saved to the database.
	
	The class saves the results in a table labled scan_<timestamp> where
	<timestamp> is the current unix-time (seconds since 1970). 

	@see: U{sqlite3 module<http://docs.python.org/library/sqlite3.html>}
		integrated with python.
	"""

	def __init__( self, path ):
		"""
		Constructor. This method creates a table to saves the scan.
		"""
		self.table = 'scan_' + str( int( time.time() ) )
		self.path = path
		self.cache = []
		conn = sqlite3.connect( self.path )
		c = conn.cursor()
		c.execute( '''create table %s (
			url STRING,
			format STRING )''' %(self.table) )
		conn.commit()
		c.close()

		self.queue = queue.Queue()
		t = Thread( target=self.worker )
		t.setDaemon( True )
		t.start()

	def add( self, url, format ):
		"""
		This method should be used to add results to the database. Also
		updates the cache.
		"""

		# update the cache
		if not url in self.cache:
			self.cache.append( url )
			if len( self.cache ) > options.get( 'cache_size' ):
				del self.cache[0]

		self.queue.put( (url, format ) )

	def worker( self ):
		"""
		Main worker function working the queue.
		"""
		while True:
			url, format = self.queue.get( 10.0 )
#			print( "sqlite: %s: %s" %( url, format ) )
			conn = sqlite3.connect( self.path )
			c = conn.cursor()
			c.execute( """INSERT INTO %s values(?, ?)"""%(self.table), (url, format) )
			conn.commit()
			c.close()
			self.queue.task_done()

	def have_it( self, url ):
		"""
		Ask if we have already saved this URL in the database. Only hits
		the database if the URL is not the cache.
		"""
		if url in self.cache:
#			print( "Cache Hit: %s (current size: %s)"%(url, len(self.cache)) )
			return True

		conn = sqlite3.connect( self.path )
		c = conn.cursor()
		c.execute( """SELECT * FROM %s WHERE url=?"""%(self.table), (url,) )
		result = c.fetchone()
		conn.commit()
		c.close()
		if not result:
			return False
		else:	
			return True
