import os, tempfile, subprocess
import xml.etree.ElementTree as etree

class backend( object ):
	"""
	This format detector backend uses
	U{FITS<http://code.google.com/p/fits/>} to detect file formats. Note
	that this backend is *very* slow. If you use this backend, you must also
	set the environment variable FITS_PATH to point to the directory where
	fits.sh is located.

	@TODO: make this windows compatible.
	@see: L{techwatch.file}
	"""
	def __init__( self ):
		"""
		Constructor. 

		@raises RuntimeError: If FITS_PATH is not set or set
		incorrectly.
		"""
		if 'FITS_PATH' not in os.environ.keys():
			raise RuntimeError( "Environment variable FITS_PATH not set" )

		self.path = os.environ['FITS_PATH']
		if not os.path.exists( self.path + '/fits.sh' ):
			raise RuntimeError( "%s not found" %(self.path) )
		self.bin = self.path + '/fits.sh' 

	def detect( self, data ):
		"""
		Detect the fileformat of the data.

		@return: The file format detected.
		@see: L{techwatch.file}
		"""
		fd, name = tempfile.mkstemp()
		f = os.fdopen( fd, 'w+b' )
		f.write( data )
		f.flush()
		
		fd_o, name_o = tempfile.mkstemp()

		cmd = [ self.bin, '-i', name, '-o', name_o ]
#		print( ' '.join( cmd ) )
		p = subprocess.Popen( cmd )
		p.communicate()

		parser = fits_parser( name_o )
		self.format = parser.parse()
#		print( self.format )

		os.remove( name )
		os.remove( name_o )
		return self.format

	def ishtml( self ):
		"""
		Detect if the detected fileformat is parseable HTML.

		@return: The file format detected.
		@see: L{techwatch.file}
		"""
		if self.format == 'Hypertext Markup Language':
			return True
		elif self.format == 'XHTML':
			return True
		print( "HTML: %s" %(self.format) )
		return False

class fits_parser( object ):
	"""
	Class responsible for parsing the output files created by FITS.
	"""

	def __init__( self, path ):
		"""
		Constructor.

		@param path: The path to the file created by FITS.
		@type  path: string
		"""
		self.path = path

	def parse( self ):
		"""
		Actual XML parser method. If the tools called by FITS do not
		agree (and FITS does not reach a definitive conclusion), the
		conclusion reached by the majority of tools is returned.

		@return: The file format detected.
		@raise RuntimeError: If FITS returned an unknown error status.
		"""
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
		elif status == 'PARTIAL':
			print( "Warning: Partial status does not make sense in this context" )
		else:
			raise RuntimeError( "fits returned unknown status '%s'" %(status) )
