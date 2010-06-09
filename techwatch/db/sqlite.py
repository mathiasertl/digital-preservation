import os, time, sqlite3, queue
from threading import Thread

class backend(object):
	def __init__( self, path ):
		self.table = 'scan_' + str( int( time.time() ) )
		self.path = path
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
		self.queue.put( (url, format ) )

	def worker( self ):
		while True:
			url, format = self.queue.get( 10.0 )
			print( "sqlite: %s: %s" %( url, format ) )
			conn = sqlite3.connect( self.path )
			c = conn.cursor()
			c.execute( """INSERT INTO %s values(?, ?)"""%(self.table), (url, format) )
			conn.commit()
			c.close()
			self.queue.task_done()

	def have_it( self, url ):
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
