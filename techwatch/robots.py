from urllib import robotparser

class robots( object ):
	inst = None

	def __init__( self ):
		self.robots = {}

	def add_url( self, domain, url ):
		if domain in self.robots.keys():
			return

		self.robots[domain] = robotparser.RobotFileParser()
		self.set_url( domain, url )
		self.read( domain )

	def set_url( self, domain, url ):
		self.robots[domain].set_url( url )

	def read( self, domain ):
		self.robots[domain].read()

	def parse( self, domain, lines ):
		self.robots[domain].parse(lines)

	def can_fetch( self, domain, useragent, url ):
		return self.robots[domain].can_fetch( useragent, url )

	def mtime( self, domain ):
		self.robots[domain].mtime()

	def modified( self, domain ):
		self.robots[domain].mtime()

def get_instance():
	if robots.inst == None:
		robots.inst = robots()
	return robots.inst

