import os, tempfile, subprocess
import xml.etree.ElementTree as etree

class fits( object ):
	def __init__( self ):
		if 'FITS_PATH' not in os.environ.keys():
			raise RuntimeError( "Environment variable FITS_PATH not set" )

		self.path = os.environ['FITS_PATH']
		if not os.path.exists( self.path + '/fits.sh' ):
			raise RuntimeError( "%s not found" %(self.path) )
		self.bin = self.path + '/fits.sh' 

	def detect( self, data ):
		fd, name = tempfile.mkstemp()
		f = os.fdopen( fd, 'w+b' )
		f.write( data )
		f.flush()
		
		fd_o, name_o = tempfile.mkstemp()

		cmd = [ self.bin, '-i', name, '-o', name_o ]
		print( ' '.join( cmd ) )
		p = subprocess.Popen( cmd )
		p.communicate()

		parser = fits_parser( name_o )
		self.format = parser.parse()
		print( self.format )

		os.remove( name )
		os.remove( name_o )
		return self.format

	def ishtml( self ):
		if self.format == 'Hypertext Markup Language':
			return True
		return False

class fits_parser( object ):
	def __init__( self, path ):
		self.path = path

	def parse( self ):
		tree = etree.parse( self.path )
		root_node = tree.getroot()
		ident_node = root_node.find( '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}identification' )
		
		status = ident_node.attrib['status']
		if status == 'SINGLE_RESULT':
			return ident_node[0].attrib['format']
		elif status == 'CONFLICT':
			num_tools = 0
			node = None
			for child in ident_node:
				if len( child ) > num_tools:
					num_tools = len(child)
					node = child
			return node.attrib['format']
		else:
			raise RuntimeError( "fits returned unknown status '%s'" %(status) )
